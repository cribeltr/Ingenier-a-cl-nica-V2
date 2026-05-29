#!/usr/bin/env node
/*
 * PRUEBA DE HUMO de HHHA — camino crítico de la app, sin abrir el navegador.
 * Verifica que, tras generar app.html, lo básico funcione:
 *   1) Importar un respaldo de data/ no da errores al cargar.
 *   2) La lista de Equipos se ve COMPLETA (no vacía).
 *   3) El filtro por la columna Modelo (que a veces trae números) funciona.
 *   4) Se abre la ficha de un equipo.
 *   5) Ctrl+K (buscador) encuentra un equipo.
 *   6) El folio se hereda del ciclo abierto del equipo.
 *
 * Uso:   node tools/smoke_test.js [app.html] [data/respaldo.json]
 * Requiere jsdom una sola vez:   npm install jsdom
 * Devuelve código 0 si todo pasa; 1 si algo del camino crítico falla.
 */
const fs = require('fs');
const path = require('path');

// --- localizar jsdom (instalado local, global, o en /tmp del entorno de build) ---
let JSDOM, VirtualConsole;
(function loadJsdom(){
  const tries = ['jsdom', '/tmp/node_modules/jsdom',
    path.join(__dirname, '..', 'node_modules', 'jsdom')];
  for(const t of tries){ try{ ({JSDOM, VirtualConsole} = require(t)); return; }catch(e){} }
  console.error('✗ Falta jsdom. Instálalo una vez con:  npm install jsdom');
  process.exit(2);
})();

const ROOT = path.join(__dirname, '..');
const APP = process.argv[2] || path.join(ROOT, 'app.html');
const STORAGE_KEY = 'hhha_v1_data';

// Respaldo: el indicado, o el primero de data/ que tenga algún ciclo abierto.
function elegirRespaldo(){
  if(process.argv[3]) return process.argv[3];
  const dir = path.join(ROOT, 'data');
  const files = fs.readdirSync(dir).filter(f=>f.endsWith('.json')).sort();
  for(const f of files){
    try{ const d = JSON.parse(fs.readFileSync(path.join(dir,f),'utf8'));
      if((d.ciclos||[]).some(c=>c.estado==='abierto')) return path.join(dir,f);
    }catch(e){}
  }
  return path.join(dir, files[0]);
}
const BACKUP = elegirRespaldo();

const html = fs.readFileSync(APP, 'utf8');
const backupRaw = fs.readFileSync(BACKUP, 'utf8');
const backup = JSON.parse(backupRaw);
const cicloAbierto = (backup.ciclos||[]).find(c=>c.estado==='abierto') || null;

const loadErrors = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => loadErrors.push((e.detail?(e.detail.stack||e.detail):e.message).toString().split('\n')[0]));

const dom = new JSDOM(html, {
  runScripts: 'dangerously', pretendToBeVisual: true,
  url: 'http://localhost/app.html', virtualConsole: vc,
  beforeParse(w){
    w.localStorage.setItem(STORAGE_KEY, backupRaw);
    w.confirm = () => true; w.alert = () => {}; w.scrollTo = () => {};
    w.matchMedia = w.matchMedia || (()=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}}));
  }
});
const { window } = dom;
const doc = window.document;

const results = [];
const check = (nombre, cond, detalle='') => { results.push({nombre, ok: !!cond, detalle}); };

setTimeout(() => {
  // 1) Carga del respaldo sin errores
  check('Importar respaldo sin errores', loadErrors.length === 0, loadErrors.join(' | '));

  // 2) Lista de Equipos completa
  let equiposRows = 0, equiposTotal = 0, equiposErr = null;
  try{
    window.navigate('equipos', {});
    const main = doc.querySelector('#main');
    equiposRows = main.querySelectorAll('table tbody tr').length;
    const m = (main.querySelector('.muted')||{}).textContent || '';
    equiposTotal = parseInt((m.match(/(\d+)\s+equipos/)||[])[1] || '0', 10);
  }catch(e){ equiposErr = e.message; }
  check('Lista de Equipos se ve completa', !equiposErr && equiposRows > 0 && equiposTotal >= 100,
    equiposErr || `filas=${equiposRows}, total=${equiposTotal}`);

  // 3) Filtro por columna Modelo con un valor numérico (el bug histórico)
  let filtroRows = -1, filtroErr = null, valorNum = null;
  try{
    window.navigate('equipos', {});
    const main = doc.querySelector('#main');
    const selects = [...main.querySelectorAll('thead select')];
    let sel = null;
    for(const s of selects){ const o = [...s.options].find(o=>/^\d+$/.test(o.value)); if(o){ sel=s; valorNum=o.value; break; } }
    if(sel){ sel.value = valorNum; sel.dispatchEvent(new window.Event('change'));
      filtroRows = main.querySelectorAll('table tbody tr').length;
    }
  }catch(e){ filtroErr = e.message; }
  check('Filtro por columna numérica (Modelo) funciona',
    !filtroErr && (valorNum===null || filtroRows > 0),
    filtroErr || (valorNum===null ? 'sin valor numérico que probar (ok)' : `Modelo=${valorNum} → ${filtroRows} filas`));

  // 4) Abrir ficha de un equipo
  let fichaOk = false, fichaErr = null;
  const invDemo = (backup.equipos && backup.equipos[0] && backup.equipos[0].inv) || null;
  try{
    window.navigate('equipo', {inv: invDemo});
    const main = doc.querySelector('#main');
    const h2 = main.querySelector('h2');
    fichaOk = !!h2 && h2.textContent.includes(invDemo) && main.innerHTML.length > 500;
  }catch(e){ fichaErr = e.message; }
  check('Abrir ficha del equipo', fichaOk, fichaErr || `inv=${invDemo}`);

  // 5) Ctrl+K (buscador global)
  let qkOk = false, qkErr = null;
  try{
    if(typeof window.quickSearch === 'function'){
      window.quickSearch();
      const modal = doc.querySelector('.modal');
      const inp = modal && modal.querySelector('input');
      const frag = (invDemo||'').replace(/^\D+/,'').slice(-5) || (invDemo||'');
      if(inp){ inp.value = frag; inp.dispatchEvent(new window.Event('input'));
        qkOk = new RegExp(frag).test(modal.textContent||'');
      }
    }
  }catch(e){ qkErr = e.message; }
  check('Ctrl+K busca y encuentra un equipo', qkOk, qkErr || `buscó "${(invDemo||'')}"`);

  // 6) Folio heredado del ciclo abierto
  let folioOk = null, folioErr = null;
  try{
    if(cicloAbierto && typeof window.folioCicloControl === 'function' && typeof window.ciclosAbiertosDe === 'function'){
      const ctrl = window.folioCicloControl(window.ciclosAbiertosDe(cicloAbierto.inv));
      folioOk = ctrl && ctrl.value === cicloAbierto.folio;
    } else { folioOk = true; folioErr = 'sin ciclo abierto en el respaldo (no aplica)'; }
  }catch(e){ folioErr = e.message; folioOk = false; }
  check('Folio se hereda del ciclo abierto', folioOk,
    folioErr || `${cicloAbierto?cicloAbierto.inv:''} → ${cicloAbierto?cicloAbierto.folio:''}`);

  // --- Reporte ---
  const fall = results.filter(r=>!r.ok);
  console.log('\nPRUEBA DE HUMO HHHA  ·  respaldo: ' + path.basename(BACKUP));
  console.log('─'.repeat(60));
  for(const r of results) console.log(`  ${r.ok?'✅':'❌'}  ${r.nombre}${r.detalle?('   ('+r.detalle+')'):''}`);
  console.log('─'.repeat(60));
  if(fall.length===0) console.log(`✅ TODO OK — ${results.length} chequeos del camino crítico pasaron.\n`);
  else console.log(`❌ FALLARON ${fall.length} de ${results.length}. Revisa antes de entregar.\n`);
  dom.window.close();
  process.exit(fall.length===0 ? 0 : 1);
}, 2000);
