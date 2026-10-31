#!/usr/bin/env python3
"""Parse all pinned bodies, failing on either ERROR or MISSING nodes."""
import hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def cli():return os.environ.get('TREE_SITTER','tree-sitter')
def check(files):
 result=subprocess.run([cli(),'parse','--grammar-path',str(ROOT),'-q',*map(str,files)],cwd=ROOT,capture_output=True,text=True)
 if result.returncode or 'ERROR' in result.stdout or 'MISSING' in result.stdout:
  print(result.stdout+result.stderr);raise SystemExit(1)
 return result
if __name__=='__main__':
 folder=ROOT/'test/fixtures/conformance';manifest=json.loads((folder/'manifest.json').read_text())
 files=[]
 for case in manifest['cases']:
  file=folder/case['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==case['sha256'],case['file'];files.append(file)
 assert set(folder.glob('*.lmcode'))==set(files),'unindexed or missing fixture'
 files += sorted((ROOT/'test/fixtures').glob('*.lmcode'))
 check(files)
 print('PASS zero ERROR/MISSING:',len(files),'documents; pinned bodies:',len(manifest['cases']))
