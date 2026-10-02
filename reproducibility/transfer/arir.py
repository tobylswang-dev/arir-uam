#!/usr/bin/env python3
"""Admission--Release Interaction Report: reference implementation, not an assessment standard.
python arir.py --runs runs --output report
Input JSONL summaries with C/X/U/N, input and canonical trajectory hashes.
Optional --events reads diagnostic JSON(.gz) files with events/fates.
"""
from pathlib import Path
import argparse,json,gzip
import numpy as np
import pandas as pd
from scipy.stats import t
KEY=['demand','B','node','link','seed'];SET=['demand','B','node','link']
MODES=['joint','vertiport_only','corridor_only','omit_both'];POL=['bypass','fifo']

def analyse(rows,out,bootstrap=4000):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    a=pd.DataFrame(rows)
    required=KEY+['policy','mode','N','C','X','U','request_sha256','trajectory_sha256']
    if any(c not in a for c in required):raise ValueError('Missing required columns')
    if a.duplicated(KEY+['policy','mode']).any():raise ValueError('Duplicate run key')
    if not ((a.N==a.C+a.X+a.U)&(a.N>0)&(a[['C','X','U']]>=0).all(axis=1)).all():raise ValueError('Conservation or nonnegative counts failed')
    for _,g in a.groupby(['demand','seed']):
        if g.N.nunique()!=1 or g.request_sha256.nunique()!=1:raise ValueError('Pairing requires identical demand and request hash')
    invariants=[]
    for mode,keys in [('vertiport_only',['demand','seed','B','node']),('corridor_only',['demand','seed','B','link','policy']),('omit_both',['demand','seed'])]:
        for k,g in a[a['mode']==mode].groupby(keys):
            invariants.append(dict(mode=mode,group=str(k),comparisons=len(g),hash_agreement=bool(g.trajectory_sha256.nunique()==1)))
    seedrows=[]
    for key,g in a.groupby(KEY):
        if len(g)!=8 or set(zip(g.policy,g['mode']))!=set((s,m) for s in POL for m in MODES):raise ValueError('Incomplete 2x2x2 block')
        z=g.set_index(['policy','mode']);r=dict(zip(KEY,key));r['N']=int(g.N.iloc[0])
        for s in POL:
            j,l,n,o=[float(z.loc[(s,m),'C']) for m in MODES]
            r['G_'+s]=100*(l-n)/r['N'];r['DL_'+s]=l-j;r['DN_'+s]=n-j
            r['H_'+s]=j-l-n+o
            # Average presence effects, with equal weights on the other gate.
            r['node_presence_'+s]=.5*((j-n)+(l-o))
            r['link_presence_'+s]=.5*((j-l)+(n-o))
        r['delta_G']=r['G_fifo']-r['G_bypass'];r['T']=r['H_fifo']-r['H_bypass']
        r['IL']=r['DL_fifo']-r['DL_bypass'];r['IN']=r['DN_fifo']-r['DN_bypass']
        r['strict_seed_reversal']=r['G_bypass']*r['G_fifo']<0
        r['either_tie']=r['G_bypass']==0 or r['G_fifo']==0
        seedrows.append(r)
    seeds=pd.DataFrame(seedrows);seeds.to_csv(out/'seed_estimands.csv',index=False)
    rng=np.random.default_rng(20260928);settings=seeds.groupby(SET,sort=True);family=2*len(settings);summary=[]
    metrics=['G_bypass','G_fifo','delta_G','DL_bypass','DL_fifo','DN_bypass','DN_fifo','IL','IN','H_bypass','H_fifo','T','node_presence_bypass','node_presence_fifo','link_presence_bypass','link_presence_fifo']
    for key,g in settings:
        r=dict(zip(SET,key));n=len(g)
        if n<2:raise ValueError('At least two independent request sets required for intervals')
        sample=rng.integers(0,n,(bootstrap,n));r.update(n=n,seed_reversals=int(g.strict_seed_reversal.sum()),seed_ties=int(g.either_tie.sum()))
        for m in metrics:
            x=g[m].to_numpy(float);r[m]=float(x.mean())
            lo,hi=np.quantile(x[sample].mean(axis=1),[.025,.975]);r[m+'_lo']=lo;r[m+'_hi']=hi
            if m in ('delta_G','T'):
                half=t.ppf(1-.05/(2*family),n-1)*x.std(ddof=1)/np.sqrt(n)
                r[m+'_family_lo']=x.mean()-half;r[m+'_family_hi']=x.mean()+half
            if m in ('G_bypass','G_fifo'):
                for label,pred in [('positive',x>0),('negative',x<0),('zero',x==0)]:r[m+'_'+label]=int(pred.sum())
        r['mean_reversal']=r['G_bypass']*r['G_fifo']<0;summary.append(r)
    summary=pd.DataFrame(summary);summary.to_csv(out/'grid_summary.csv',index=False)
    flat=a.drop(columns=[c for c in ['scan_counts','fifo_eligible_visits_by_fate','ever_fifo_eligible_requests_by_fate'] if c in a])
    flat.to_csv(out/'absolute_runs.csv',index=False)
    a.groupby(SET+['policy','mode'])[['N','C','X','U','WC']].mean().reset_index().to_csv(out/'absolute_means.csv',index=False)
    pd.DataFrame(invariants).to_csv(out/'invariance_checks.csv',index=False)
    # Preserve units: visit counts and counts of exposed requests, never completion-loss components.
    diag=[]
    for r in rows:
        d={k:r[k] for k in KEY+['policy','mode']}
        for src,prefix in [('scan_counts','visits_'),('fifo_eligible_visits_by_fate','fifo_visits_fate_'),('ever_fifo_eligible_requests_by_fate','exposed_requests_fate_')]:
            for k,v in r.get(src,{}).items():d[prefix+k]=v
        diag.append(d)
    dg=pd.DataFrame(diag).fillna(0);dg.to_csv(out/'scan_diagnostics.csv',index=False)
    counts=summary.groupby(['demand','B']).agg(mean_reversal_cells=('mean_reversal','sum'),settings=('mean_reversal','size'),paired_seed_reversals=('seed_reversals','sum')).reset_index()
    restriction=seeds.groupby(['demand','B','seed','link']).delta_G.agg(lambda x:float(x.max()-x.min())).max()
    result=dict(actual_runs=len(a),request_sets=len(a[['demand','seed']].drop_duplicates()),settings=len(summary),invariant_groups=len(invariants),invariant_failures=sum(not i['hash_agreement'] for i in invariants),max_node_spread_delta_G=float(restriction),family_effects=family,mean_reversals=counts.to_dict('records'))
    (out/'CHECKS.json').write_text(json.dumps(result,indent=2))
    lines=['# Admission--Release Interaction Report','',f"{len(a):,} actual simulation records; {result['request_sets']} distinct demand sets; {len(summary)} settings.",'', '## Observed-grid mean reversals','','| '+' | '.join(counts.columns)+' |\n| '+' | '.join(['---']*len(counts.columns))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in counts.itertuples(index=False,name=None)),'','## Interpretation','',f"Canonical trajectory agreement failures: {result['invariant_failures']} across {len(invariants)} groups. These are supplied-hash agreement checks under the stated model assumptions, not independent proof or authenticity verification.",f"Maximum seed-wise node-rate spread in delta G: {restriction:.3g} pp.",'','G uses generated demand. Joint cancels from G. Under omit-links invariance, IL is minus the change in joint. H is the node/link presence difference-in-differences; T is its FIFO-minus-bypass change. Neither is calibrated operational synergy.','',f"Primary family: {family} delta-G/T means, Bonferroni t intervals; pointwise paired percentile bootstrap intervals use {bootstrap} resamples. Independence is between request sets, not between matched runs. Mean-reversal counts and seed frequencies are descriptive.",'','Scan states count request-scan visits. A request may have many visits. Exposure by final fate is associative; it is not a causal decomposition of lost completions.','', 'The current model fixes topology, paths, timing, demand generator and eligibility. Generalisation to other simulators, operators or physical services is untested.']
    (out/'REPORT.md').write_text('\n'.join(lines))
    return result

def audit_events(folder,out):
    rows=[]
    for p in sorted(Path(folder).glob('*.json*')):
        opener=gzip.open if p.suffix=='.gz' else open
        with opener(p,'rt') as f:d=json.load(f)
        fates={f['fid']:f['fate'] for f in d['fates']};seen=set();counts={}
        for e in d['events']:
            key=(e['t'],e['fid'])
            if key in seen:raise ValueError('Duplicate request-scan state')
            seen.add(key)
            if e['fid'] not in fates:raise ValueError('Event without final fate')
            if e['state']=='fifo_eligible' and not(e['node_ok'] and e['link_ok']):raise ValueError('Ineligible FIFO-exposure label')
            counts[e['state']]=counts.get(e['state'],0)+1
        rows.append(dict(file=p.name,visits=len(seen),counts=counts))
    Path(out).write_text(json.dumps(rows,indent=2));return len(rows)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--runs',required=True);p.add_argument('--output',required=True);p.add_argument('--events');args=p.parse_args()
    rows=[json.loads(line) for f in sorted(Path(args.runs).glob('*.jsonl')) for line in f.read_text().splitlines() if line.strip()]
    print(json.dumps(analyse(rows,args.output),indent=2))
    if args.events:print('Full event files checked',audit_events(args.events,Path(args.output)/'EVENT_CHECKS.json'))
