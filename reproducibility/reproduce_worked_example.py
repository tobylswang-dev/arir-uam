from pathlib import Path
import json,statistics
root=Path(__file__).resolve().parent
rows=[json.loads(line) for p in sorted((root/'runs').glob('*.jsonl')) for line in p.read_text().splitlines() if line.strip()]
r=[x for x in rows if (x['demand'],x['B'],x['node'],x['link'])==(1,2,1,1.5)]
assert len(r)==800 and {x['seed'] for x in r}==set(range(20000,20100))
for seed in range(20000,20100):
 s=[x for x in r if x['seed']==seed]
 assert len({(x['policy'],x['mode']) for x in s})==8
 assert len({x['request_sha256'] for x in s})==1
 assert all(x['N']==x['C']+x['X']+x['U'] for x in s)
means={p:{m:statistics.mean(x['C'] for x in r if x['policy']==p and x['mode']==m) for m in ['joint','vertiport_only','corridor_only','omit_both']} for p in ['bypass','fifo']}
expected={'bypass':[721.84,702.11,782.95,920.85],'fifo':[662.53,702.11,694.44,920.85]}
for p in means:
 assert list(means[p].values())==expected[p]
dl={p:round(means[p]['vertiport_only']-means[p]['joint'],2) for p in means}
assert dl=={'bypass':-19.73,'fifo':39.58}
result={'records':800,'demand_sets':100,'mean_completions':means,'D_L':dl,'I_L':round(dl['fifo']-dl['bypass'],2),'scope':'stored-summary worked-example reproduction; no simulator rerun'}
(root/'WORKED_EXAMPLE_CHECK.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
