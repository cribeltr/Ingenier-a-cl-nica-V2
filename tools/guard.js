#!/usr/bin/env node
/*
 * GUARDIÁN (autocorrección) de HHHA.
 * Corre solo tras `python3 build_app.py`. Bloquea (sale con código 1) las CLASES de error
 * que ya se cometieron en el proyecto, para que no se repitan:
 *
 *   1. Patrón incompleto: el estado de una MP DEBE derivarse de estadoMPDesdeResultado en
 *      TODOS los lugares que crean/guardan una MP (no fórmulas sueltas). [causa del bug v0.45]
 *   2. Patrones legacy prohibidos (la vieja fórmula de estado). [v0.45]
 *   3. Todas las vistas deben dibujarse SIN error con un respaldo real. [v0.39: lista vacía]
 *   4. (Aviso) Funciones definidas y nunca usadas (código muerto). [v0.40: renderResumenEquipo]
 *   5. (Aviso) Reglas CSS de layout sobre una clase usada por >1 tabla (riesgo de romper
 *      otra vista). [v0.42/0.47: eq-grid compartida]
 *
 * Uso:  node tools/guard.js [app.html]
 * Requiere jsdom (una vez): npm install jsdom
 */
const fs = require('fs');
const path = require('path');
let JSDOM, VirtualConsole;
(function(){ const t=['jsdom','/tmp/node_modules/jsdom',path.join(__dirname,'..','node_modules','jsdom')];
  for(const x of t){ try{ ({JSDOM,VirtualConsole}=require(x)); return; }catch(e){} }
  console.error('✗ Falta jsdom. Instálalo: npm install jsdom'); process.exit(2); })();

const ROOT = path.join(__dirname, '..');
const SRC  = fs.readFileSync(path.join(ROOT,'build_app.py'),'utf8');
const APP  = process.argv[2] || path.join(ROOT,'app.html');

const fatales = [];   // bloquean
const avisos  = [];   // informan, no bloquean
const ok      = [];

function lineaDe(idx){ return SRC.slice(0,idx).split('\n').length; }

// --- 1. El estado de una MP debe derivarse de estadoMPDesdeResultado en todo sitio que cree MP ---
{
  const re = /tipo:\s*'Mantención preventiva'/g; let m, sitios=0, malos=[];
  while((m = re.exec(SRC))){
    sitios++;
    const ventana = SRC.slice(m.index, m.index + 600);
    const em = ventana.match(/estado:\s*([^,\n]+)/);
    if(em){
      const val = em[1].trim();
      const okVal = val.startsWith('estadoMPDesdeResultado') || val === "'baja'" || val === '"baja"';
      if(!okVal) malos.push(`línea ${lineaDe(m.index)}: estado = ${val}`);
    }
  }
  if(malos.length) fatales.push('Estado de MP NO derivado de estadoMPDesdeResultado en '+malos.length+' sitio(s):\n      '+malos.join('\n      '));
  else ok.push(`Estado de MP derivado del resultado en los ${sitios} sitios que crean MP`);
}

// --- 2. Patrones legacy prohibidos ---
{
  const prohibidos = [
    ["eq.estado||'operativo'", 'fórmula vieja de estado de MP (usa estadoMPDesdeResultado)'],
    ["eq.estado || 'operativo'", 'fórmula vieja de estado de MP (usa estadoMPDesdeResultado)'],
    ['new Date(f)', "fecha cruda sin 'T00:00:00' (invariante de zona horaria)"]
  ];
  let hubo=false;
  for(const [pat,desc] of prohibidos){
    let i=SRC.indexOf(pat);
    while(i!==-1){ fatales.push(`Patrón prohibido en línea ${lineaDe(i)}: «${pat}» → ${desc}`); hubo=true; i=SRC.indexOf(pat,i+1); }
  }
  if(!hubo) ok.push('Sin patrones legacy prohibidos');
}

// --- 4. Funciones definidas y nunca usadas (aviso) ---
{
  // Quitar comentarios para no contar menciones en el CHANGELOG/notas como "usos".
  const CODE = SRC
    .replace(/<!--[\s\S]*?-->/g,' ')
    .replace(/\/\*[\s\S]*?\*\//g,' ')
    .replace(/(?<!:)\/\/[^\n]*/g,' ');
  const defs = [...CODE.matchAll(/\bfunction\s+([a-zA-Z_][\w]*)\s*\(/g)].map(m=>m[1]);
  const muertas = [];
  for(const name of defs){
    if(name.length < 2) continue; // saltar helpers de 1 letra ($,_)
    const usos = (CODE.match(new RegExp('\\b'+name+'\\b','g'))||[]).length;
    if(usos <= 1) muertas.push(name);
  }
  if(muertas.length) avisos.push('Funciones definidas y nunca usadas (código muerto): '+muertas.join(', '));
  else ok.push('Sin funciones muertas');
}

// --- 5. Clases CSS con layout AGRESIVO usadas por >1 tabla (aviso) ---
{
  // Solo props que pueden romper otra vista (no el width:100% base, que es inofensivo).
  const layoutProps = /(word-break|overflow-wrap|table-layout)/;
  const cssClases = new Set();
  for(const m of SRC.matchAll(/\.([a-zA-Z][\w-]*)\s*(,[^\{]*)?\{([^}]*)\}/g)){
    if(layoutProps.test(m[3])) cssClases.add(m[1]);
  }
  const sospechosas = [];
  for(const cls of cssClases){
    const tablas = (SRC.match(new RegExp("el\\('table',\\{class:'[^']*\\b"+cls+"\\b","g"))||[]).length;
    if(tablas > 1) sospechosas.push(`${cls} (en ${tablas} tablas)`);
  }
  if(sospechosas.length) avisos.push('Clases CSS con layout agresivo compartidas por varias tablas (riesgo de romper otra vista): '+sospechosas.join(', '));
  else ok.push('Sin clases de layout agresivo compartidas entre tablas');
}

// --- 3. Todas las vistas se dibujan sin error con un respaldo real ---
function elegirRespaldo(){
  const dir = path.join(ROOT,'data');
  const files = fs.readdirSync(dir).filter(f=>f.endsWith('.json')).sort();
  // preferir el más reciente/grande
  return path.join(dir, files[files.length-1]);
}
const BACKUP = elegirRespaldo();
const html = fs.readFileSync(APP,'utf8');
const backupRaw = fs.readFileSync(BACKUP,'utf8');
const backup = JSON.parse(backupRaw);
const vistas = [...SRC.matchAll(/VIEWS\.([a-zA-Z]+)\s*=\s*function/g)].map(m=>m[1]);
const errs=[]; const vc=new VirtualConsole();
vc.on('jsdomError', e=>errs.push((e.detail?(e.detail.stack||e.detail):e.message).toString().split('\n')[0]));
const dom = new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,url:'http://localhost/a.html',virtualConsole:vc,
  beforeParse(w){ w.localStorage.setItem('hhha_v1_data',backupRaw); w.confirm=()=>true; w.alert=()=>{}; w.scrollTo=()=>{};
    w.matchMedia=()=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}}); }});
const { window } = dom;

setTimeout(()=>{
  const rotas = [];
  const invDemo = backup.equipos && backup.equipos[0] && backup.equipos[0].inv;
  for(const v of vistas){
    const antes = errs.length;
    try{
      window.navigate(v, v==='equipo' ? {inv:invDemo} : {});
      const main = window.document.querySelector('#main');
      if(!main || main.innerHTML.length < 30) rotas.push(`${v} (vista vacía)`);
    }catch(e){ rotas.push(`${v}: ${(e.message||'').split('\n')[0]}`); }
    if(errs.length > antes) rotas.push(`${v}: ${errs.slice(antes).join(' | ')}`);
  }
  if(rotas.length) fatales.push('Vistas que fallan al dibujarse:\n      '+rotas.join('\n      '));
  else ok.push(`Las ${vistas.length} vistas se dibujan sin error`);

  // --- Reporte ---
  console.log('\nGUARDIÁN HHHA  ·  respaldo: '+path.basename(BACKUP));
  console.log('─'.repeat(60));
  ok.forEach(o=>console.log('  ✅  '+o));
  avisos.forEach(a=>console.log('  ⚠️   '+a));
  fatales.forEach(f=>console.log('  ❌  '+f));
  console.log('─'.repeat(60));
  if(fatales.length===0) console.log(`✅ GUARDIÁN OK${avisos.length?(' (con '+avisos.length+' aviso(s))'):''}.\n`);
  else console.log(`❌ GUARDIÁN: ${fatales.length} problema(s) que BLOQUEAN. Corrige antes de entregar.\n`);
  dom.window.close();
  process.exit(fatales.length===0 ? 0 : 1);
}, 2000);
