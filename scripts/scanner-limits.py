#!/usr/bin/env python3
import pathlib,subprocess,tempfile,os
ROOT=pathlib.Path(__file__).resolve().parents[1]
cli=os.environ.get('TREE_SITTER','tree-sitter')
with tempfile.TemporaryDirectory(prefix='lmcode-scanner-') as tmp:
 def check(source,ok):
  f=pathlib.Path(tmp,'input.lmcode');f.write_bytes(source.encode())
  r=subprocess.run([cli,'parse','--grammar-path',str(ROOT),'-q',str(f)],cwd=ROOT,capture_output=True,text=True)
  assert (r.returncode==0)==ok,(source[:80],r.stdout,r.stderr)
 tag='T'+'a'*300
 check('let x=<<'+tag+';\nbody\n'+tag+'\n',True)
 tags=['T'+str(i) for i in range(80)]
 check('many('+','.join('<<'+t for t in tags)+');\n'+''.join('body\n'+t+'\n' for t in tags),True)
 check('let x=<<TAG;\r\nbody\r\nTAG\r\n',True)
 check('let x=<<TAG;\nTAG',True)
 tag='T'+'a'*1100
 check('let x=<<'+tag+';\nbody\n'+tag+'\n',False)
print('PASS long tags, 80 queued bodies, CRLF, EOF closer and capacity refusal')
