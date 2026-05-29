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

  // 3) Filtro de columna estilo Excel: buscador + marcar uno/varios valores
  let filtroErr = null, filtroDet = '', filtroOk = false;
  try{
    window.navigate('equipos', {});
    let main = doc.querySelector('#main');
    const total = main.querySelectorAll('tbody tr.row-click').length;
    const btn = main.querySelector('thead tr.filtros-col th .col-filter-btn');
    btn.click();
    const pop = doc.querySelector('.col-filter-pop');
    const tieneBuscador = !!(pop && pop.querySelector('.cf-search'));
    const items = pop ? [...pop.querySelectorAll('.cf-item input')] : [];
    if(items.length){
      items[0].checked = true; items[0].dispatchEvent(new window.Event('change'));
      main = doc.querySelector('#main');
      const filtrado = main.querySelectorAll('tbody tr.row-click').length;
      filtroOk = tieneBuscador && filtrado > 0 && filtrado <= total;
      filtroDet = `buscador=${tieneBuscador}, ${items.length} valores, 1 marcado → ${filtrado}/${total} filas`;
    } else { filtroDet = 'sin valores para probar'; filtroOk = tieneBuscador; }
    doc.querySelectorAll('.col-filter-pop').forEach(p=>p.remove());
  }catch(e){ filtroErr = e.message; filtroOk = false; }
  check('Filtro de columna estilo Excel (buscar + marcar)', filtroOk, filtroErr || filtroDet);

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

  // 7) En Buscar equipos, hacer clic en la FILA abre la ficha (sin botón "Ficha")
  let rowOk = false, rowErr = null, sinBotonFicha = false;
  try{
    window.navigate('equipos', {});
    let main = doc.querySelector('#main');
    const tr = main.querySelector('tbody tr.row-click');
    sinBotonFicha = ![...main.querySelectorAll('tbody tr:first-child button')].some(b=>/^ficha$/i.test(b.textContent.trim()));
    if(tr){ tr.dispatchEvent(new window.MouseEvent('click', {bubbles:true}));
      main = doc.querySelector('#main');
      const h2 = main.querySelector('h2');
      rowOk = !!h2 && / · /.test(h2.textContent); // la ficha titula "Equipo · inv"
    }
  }catch(e){ rowErr = e.message; }
  check('Clic en la fila abre la ficha (sin botón Ficha)', rowOk && sinBotonFicha,
    rowErr || `abrióFicha=${rowOk}, sinBotónFicha=${sinBotonFicha}`);

  // 8) El historial de eventos tiene botón Imprimir
  let printOk = false, printErr = null;
  try{
    window.navigate('equipo', {inv: invDemo});
    const main = doc.querySelector('#main');
    printOk = typeof window.imprimirHistorial === 'function' &&
      [...main.querySelectorAll('button')].some(b=>/imprimir/i.test(b.textContent));
  }catch(e){ printErr = e.message; }
  check('Historial: existe botón Imprimir', printOk, printErr || '');

  // 9) MP con causal C1–C8 marca "R" en la programación del mes siguiente
  let causalOk = false, causalErr = null, detCausal = '';
  try{
    if(typeof window.aplicarEfectosEvento === 'function' && typeof window.findEquipo === 'function'){
      const MES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
      const eq = window.findEquipo(invDemo);
      // Buscar un mes (idx<11) cuyo mes siguiente tenga la programación vacía, para no pisar.
      let mIdx = -1;
      for(let i=0;i<11;i++){ const sig=(eq.registro||{})[MES[i+1]]||{}; if(!sig.P){ mIdx=i; break; } }
      if(mIdx>=0){
        const fecha = `2026-${String(mIdx+1).padStart(2,'0')}-10`;
        window.aplicarEfectosEvento({inv:invDemo, equipo:eq.equipo, tipo:'Mantención preventiva', resultado:'C1', fecha, id:990001, ejecutor:'PruebaHumo'});
        const sigP = ((window.findEquipo(invDemo).registro||{})[MES[mIdx+1]]||{}).P;
        causalOk = sigP === 'R';
        detCausal = `${MES[mIdx]} C1 → ${MES[mIdx+1]}.P=${sigP}`;
      } else { causalOk = true; detCausal = 'sin mes libre para probar (ok)'; }
    }
  }catch(e){ causalErr = e.message; }
  check('Causal C1–C8 marca "R" en el mes siguiente', causalOk, causalErr || detCausal);

  // 10) Una MP con causal C2 deja el equipo "en servicio técnico" (no "operativo")
  let c2Ok = false, c2Err = null, c2Det = '';
  try{
    if(typeof window.estadoMPDesdeResultado === 'function'){
      const map = {Si:'operativo', C2:'en servicio técnico', C3:'no operativo', FS:'no operativo', NU:'no operativo', Baja:'baja', C1:''};
      c2Ok = Object.entries(map).every(([r,e]) => window.estadoMPDesdeResultado(r) === e);
      c2Det = 'C2→'+window.estadoMPDesdeResultado('C2');
    }
  }catch(e){ c2Err = e.message; }
  check('MP con causal C2 → "en servicio técnico"', c2Ok, c2Err || c2Det);

  // 11) Resumen → "MP del año · por mes": clic en un mes abre Asignaciones en ESE mes
  let mesOk = false, mesErr = null, mesDet = '';
  try{
    window.navigate('asignaciones', {mes:'Feb', estadoMP:'pend'});
    const main = doc.querySelector('#main');
    const h2 = main.querySelector('h2') ? main.querySelector('h2').textContent : '';
    // el selector de mes debe quedar en Febrero (índice 1)
    const selMes = [...main.querySelectorAll('select')].find(s => [...s.options].some(o=>/Todos los meses/.test(o.textContent)) && [...s.options].some(o=>o.textContent==='Feb'));
    const mesVal = selMes ? String(selMes.value) : '?';
    const chip = main.textContent.includes('Pendientes'); // chip del drill estadoMP=pend
    mesOk = /Asignaciones/.test(h2) && mesVal === '1';
    mesDet = `vista=${h2}, mes=${mesVal} (1=Feb), chipPend=${chip}`;
  }catch(e){ mesErr = e.message; }
  check('Resumen→Asignaciones abre el mes correcto (Feb)', mesOk, mesErr || mesDet);

  // 12) El historial muestra el estado GUARDADO de la MP (Si + No operativo => No operativo)
  let histOk = false, histErr = null, histDet = '';
  try{
    if(typeof window.estadoMPFinal === 'function'){
      const a = window.estadoMPFinal('Si','no operativo');
      const b = window.estadoMPFinal('Si','operativo');
      const c = window.estadoMPFinal('C2','operativo'); // causal manda
      histOk = a==='no operativo' && b==='operativo' && c==='en servicio técnico';
      histDet = `Si/no-op→${a}, Si/op→${b}, C2→${c}`;
    }
  }catch(e){ histErr = e.message; }
  check('Historial respeta el estado elegido en la MP', histOk, histErr || histDet);

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
