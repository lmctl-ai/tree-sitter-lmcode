#!/usr/bin/env python3
"""Production-copy controls; each fault must change acceptance of a real fixture."""
import os,pathlib,shutil,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];CLI=os.environ.get('TREE_SITTER','tree-sitter')
controls=[
 ('lost heredoc state','src/scanner.c','return s->used+3;','return 0;','test/fixtures/conformance/mono--01_dsl_heredoc--0.lmcode',False),
 ('lost map entry arrow','grammar.js'," '=>',field('value'"," '->',field('value'",'test/fixtures/conformance/cpp--203-map-literals--0.lmcode',False),
 ('lost dedent','src/scanner.c','bool dedent=s->queue[2]!=0;','bool dedent=false;','test/fixtures/conformance/mono--01_dsl_heredoc--0.lmcode',False),
 ('lost splice phase','src/scanner.c','s->used&&!s->splice&&valid[HEREDOC_BODY]','s->used&&valid[HEREDOC_BODY]','test/fixtures/splices.lmcode',False),
 ('silent unfinished heredoc','grammar.js',"repeat(choice($.function_declaration,$._statement)),$.end_of_file","repeat(choice($.function_declaration,$._statement)),optional($.end_of_file)",'test/negative/unterminated-heredoc-eof.lmcode',True),
 ('lost qw words','src/scanner.c','if(valid[QW_WORD])return word(l,QW_WORD);','if(valid[QW_WORD])return false;','test/fixtures/features.lmcode',False),
]
with tempfile.TemporaryDirectory(prefix='lmcode-controls-') as tmp:
 target=pathlib.Path(tmp,'grammar');shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('.git','node_modules','__pycache__','build'))
 originals={file:(target/file).read_text() for _,file,_,_,_,_ in controls}
 def run(args):return subprocess.run([CLI,*args],cwd=target,capture_output=True,text=True)
 def parse(file):
  r=run(['parse','--grammar-path',str(target),'-q',str(target/file)])
  if r.returncode:assert 'ERROR' in r.stdout or 'MISSING' in r.stdout,(r.stdout,r.stderr)
  return r.returncode==0
 assert run(['generate']).returncode==0
 for _,_,_,_,fixture,accepts in controls:assert parse(fixture)!=accepts,('baseline',fixture)
 print('BASELINE PASS',flush=True)
 for label,file,before,after,fixture,accepts in controls:
  for name,text in originals.items():(target/name).write_text(text)
  text=originals[file];assert before in text,('anchor',label);(target/file).write_text(text.replace(before,after))
  generated=run(['generate']);assert generated.returncode==0,(label,generated.stdout,generated.stderr)
  assert parse(fixture)==accepts,('SURVIVED',label)
  print('CAUGHT '+label,flush=True)
 print('PASS '+str(len(controls))+' production-copy controls')
