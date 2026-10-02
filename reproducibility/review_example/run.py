"""Hand-constructed arithmetic/interface example; not empirical validation."""
from pathlib import Path
import sys,json,tempfile,copy
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'transfer'))
from arir import analyse
import pandas as pd
rows=[]
for seed in (1,2,3):
 for policy,counts in [('bypass',[70,80,90,100]),('fifo',[60,80,85,100])]:
  for mode,C in zip(['joint','vertiport_only','corridor_only','omit_both'],counts):
   rows.append(dict(seed=seed,demand=1.,B=2,node=1.,link=1.,policy=policy,mode=mode,N=100,C=C,X=100-C,U=0,WC=0,request_sha256=f'fixture-{seed}',trajectory_sha256=f'fixture-{seed}-{mode}'+(policy if mode in ['joint','corridor_only'] else '')))
out=Path(__file__).resolve().parent/'output';out.mkdir(exist_ok=True)
(out/'input.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
analyse(rows,out,bootstrap=50)
s=pd.read_csv(out/'seed_estimands.csv')
assert (s.IL==10).all() and (s.delta_G==5).all() and (s['T']==-5).all()
checks={}
with tempfile.TemporaryDirectory() as td:
 for name in ['conservation','missing_block','unmatched_input']:
  bad=copy.deepcopy(rows)
  if name=='conservation':bad[0]['C']+=1
  elif name=='missing_block':bad.pop()
  else:bad[0]['request_sha256']='mismatch'
  try:analyse(bad,td,bootstrap=50)
  except ValueError:checks[name]='rejected'
  else:raise AssertionError(name)
(out/'EXAMPLE_CHECKS.json').write_text(json.dumps({'fixture_only':True,'IL':10,'delta_G_pp':5,'T':-5,'malformed_inputs':checks},indent=2))
print('PASS: IL=10; delta_G=5 pp; T=-5; three malformed inputs rejected.')
