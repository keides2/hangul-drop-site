// Execute the real makeSyllables() logic from index.html against grid-mask fixtures.
// No gameplay code is mocked or rewritten; this test includes negative cases.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const file=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../index.html');
const html=fs.readFileSync(file,'utf8');
function constant(name){
  const m=html.match(new RegExp('^  const '+name+'=.*$','m'));
  assert.ok(m, 'Missing '+name);return m[0];
}
function fn(from,to){
  const a=html.indexOf('  function '+from+'('),b=html.indexOf('  function '+to+'(',a);
  assert.ok(a>=0&&b>a,from);return html.slice(a,b);
}
const context={};
vm.runInNewContext([
  constant('ONSETS'),constant('VOWELS'),constant('FINALS'),
  constant('VERTICAL'),constant('HORIZONTAL'),
  fn('compose','pairKey'),fn('pairKey','makeSyllables'),
  fn('makeSyllables','makeBatchimCandidates'),
  'globalThis.match = groups => makeSyllables(groups).map(p=>p.ch);'
].join('\n'),context);
const masks={
  'ㄷ':['111','100','111'],'ㄱ':['111','001','001'],
  'ㅏ':['010','011','010'],'ㅓ':['010','110','010'],
  'ㅗ':['010','111']
};
function group(id,j,x,y,rot=0){
  const raw=masks[j].flatMap((row,ry)=>[...row].flatMap((v,rx)=>v==='1'?[{x:rx,y:ry}]:[]));
  const minX=Math.min(...raw.map(c=>c.x)),minY=Math.min(...raw.map(c=>c.y));
  const cells=raw.map(c=>({x:x+c.x-minX,y:y+c.y-minY}));
  const w=Math.max(...cells.map(c=>c.x))-x+1,h=Math.max(...cells.map(c=>c.y))-y+1;
  return {id,j,x,y,rot,cells,w,h,right:x+w,bottom:y+h,cx:x+w/2,cy:y+h/2};
}
const tests=[
  ['notch right: ㄷ+ㅓ=더',group(1,'ㄷ',5,10),group(2,'ㅓ',7,10),['더']],
  ['normal right: ㄷ+ㅏ=다',group(1,'ㄷ',5,10),group(2,'ㅏ',8,10),['다']],
  ['notch below: ㄱ+ㅗ=고',group(1,'ㄱ',5,10),group(2,'ㅗ',5,12),['고']],
  ['normal below: ㄱ+ㅗ=고',group(1,'ㄱ',5,10),group(2,'ㅗ',5,13),['고']],
  ['wrong left',group(1,'ㄷ',5,10),group(2,'ㅓ',2,10),[]],
  ['wrong above',group(1,'ㄱ',5,10),group(2,'ㅗ',5,6),[]],
  ['real collision',group(1,'ㄷ',5,10),group(2,'ㅏ',6,10),[]],
  ['gap >1 cell',group(1,'ㄷ',5,10),group(2,'ㅏ',10,10),[]],
  ['misaligned',group(1,'ㄷ',5,10),group(2,'ㅏ',8,14),[]],
  ['rotated consonant',group(1,'ㄷ',5,10,1),group(2,'ㅏ',8,10),[]]
];
for(const [name,c,v,want] of tests){
  const got=Array.from(context.match([c,v]));
  assert.deepEqual(got,want,name+': '+JSON.stringify(got));
  console.log('PASS',name);
}
console.log('PASS',tests.length,'Hangul positioning regression cases');
