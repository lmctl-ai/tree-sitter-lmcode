#!/usr/bin/env python3
import pathlib,os,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
if __name__=='__main__':
 files=sorted((ROOT/'test/negative').glob('*.lmcode'));assert files
 for file in files:
  result=subprocess.run([os.environ.get('TREE_SITTER','tree-sitter'),'parse','--grammar-path',str(ROOT),'-q',str(file)],cwd=ROOT,capture_output=True,text=True)
  assert result.returncode!=0 and ('ERROR' in result.stdout or 'MISSING' in result.stdout),(file.name,result.stdout,result.stderr)
 print('PASS explicit syntax refusals:',len(files))
