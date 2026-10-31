// Development-only importer. CI uses the committed bodies and hashes, not private
// checkouts. The authoritative outer lexer identifies bodies without executing code.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
const [mono,lmok,cpp,spec]=process.argv.slice(2);
if(!spec)throw Error('usage: node --experimental-strip-types scripts/import-corpus.mjs MONO LMOK CPP SPEC');
const {Lexer}=await import(pathToFileURL(path.join(mono,'lmscript/lmscript.ts')));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const revision=root=>execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim();
const roots=[{name:'mono',root:mono,dir:'lmscript/examples',repo:'https://github.com/lmctlhq/lmctl-mono'},
 {name:'lmok',root:lmok,dir:'rules/lmcode',repo:'https://github.com/lmctl-ai/lmok'},
 {name:'cpp',root:cpp,dir:'sample-suite/programs',repo:'https://github.com/lmctl-ai/lmcode-cpp'}];
const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]).sort();
const target='test/fixtures/conformance';fs.mkdirSync(target,{recursive:true});
const sources=[],cases=[];
for(const root of roots){root.commit=revision(root.root);
 for(const file of walk(path.join(root.root,root.dir)).filter(f=>f.endsWith('.lms'))){
  const relative=path.relative(root.root,file),source=fs.readFileSync(file,'utf8');
  const lexer=new Lexer(source,file),tokens=lexer.tokenize();
  const errors=lexer.diagnostics.filter(d=>d.severity==='error');if(errors.length)throw Error(file+': '+JSON.stringify(errors));
  const blocks=tokens.filter(t=>t.block?.marker==='dsl');
  sources.push({origin:root.name,path:relative,sha256:sha(source),blocks:blocks.length});
  for(const [index,token]of blocks.entries()){
   if(!token.block.closed)throw Error('Unclosed source block '+file);
   const lines=token.block.lines;let first=lines[0]?.line??token.line+1,last=first-1;
   for(const line of lines){last=Math.max(last,line.line);for(const piece of line.pieces)if(typeof piece!=='string')last=Math.max(last,source.slice(0,piece.endOffset).split(/\r\n|\r|\n/).length);}
   const body=source.split(/\n/).slice(first-1,last).join('\n')+'\n';
   const name=root.name+'--'+path.basename(file,'.lms')+'--'+index+'.lmcode';
   fs.writeFileSync(path.join(target,name),body);
   cases.push({file:name,origin:root.name,source:relative,block:index,line:first,sha256:sha(body)});
  }
 }
}
const pins={mono:{repo:roots[0].repo,commit:roots[0].commit},lmok:{repo:roots[1].repo,commit:roots[1].commit},cpp:{repo:roots[2].repo,commit:roots[2].commit},spec:{repo:'https://github.com/lmctl-ai/lmcode',commit:revision(spec)}};
fs.writeFileSync('SOURCE-PINS.json',JSON.stringify(pins,null,2)+'\n');
fs.writeFileSync('MONO-PIN',roots[0].commit+'\n');
fs.writeFileSync(path.join(target,'manifest.json'),JSON.stringify({sources,cases},null,2)+'\n');
console.log(JSON.stringify({sources:sources.length,bodies:cases.length,byOrigin:Object.fromEntries(roots.map(r=>[r.name,cases.filter(c=>c.origin===r.name).length]))}));
