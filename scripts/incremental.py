#!/usr/bin/env python3
"""Compare edited/reused trees with fresh trees, including byte/row ranges."""
import os,pathlib,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
CLI=os.environ.get('TREE_SITTER','tree-sitter')
def parse(file,edits=()):
 command=[CLI,'parse','--grammar-path',str(ROOT),str(file)]
 for edit in edits:command+=['--edits',edit]
 r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
 assert r.returncode==0,(r.stdout,r.stderr)
 assert 'ERROR' not in r.stdout and 'MISSING' not in r.stdout,r.stdout
 return r.stdout
with tempfile.TemporaryDirectory(prefix='lmcode-incremental-') as tmp:
 source=b'pair(<<A, <<~B);\nalpha\nA\n  beta\n  B\nlet n = 1;\n'
 data=source;edits=[]
 def edit(at,count,text):
  global data
  edits.append(str(at)+' '+str(count)+' '+text)
  raw=text.encode();data=data[:at]+raw+data[at+count:]
 edit(0,0,'# 世界\n')
 edit(data.index(b'alpha'),5,'alpha\nA_suffix\ncontinued')
 edit(data.index(b'<<A')+2,1,'LONG_TAG')
 edit(data.index(b'\nA\n')+1,1,'LONG_TAG')
 old=pathlib.Path(tmp,'old.lmcode');fresh=pathlib.Path(tmp,'fresh.lmcode')
 old.write_bytes(source);fresh.write_bytes(data)
 assert parse(old,edits)==parse(fresh),'incremental ranges/tree diverged from fresh parse'
 # Remove the first queued literal and its body, reusing the second opener.
 source=data;edits=[]
 start=data.index(b'<<LONG_TAG');end=data.index(b'<<~B')
 edit(start,end-start,'')
 start=data.index(b'\nalpha')+1;end=data.index(b'\n  beta')+1
 edit(start,end-start,'')
 old.write_bytes(source);fresh.write_bytes(data)
 assert parse(old,edits)==parse(fresh),'queue deletion did not restore scanner state'
print('PASS incremental queue edits, renaming, deletion and UTF-8 byte ranges')
