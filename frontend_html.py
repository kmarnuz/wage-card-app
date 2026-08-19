FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wage Card Management System</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Segoe UI",Roboto,-apple-system,sans-serif;background:#f4f6f8;color:#2c3e50}
.header{background:#1e2a3a;color:#fff;padding:16px 30px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #e67e22}
.header h1{font-size:18px;font-weight:600;letter-spacing:.3px}
.header .subtitle{font-size:11px;color:#bdc3c7;margin-top:2px}
.main{padding:20px 30px;max-width:1450px;margin:0 auto}
.panel{background:#fff;border-radius:6px;padding:20px;margin-bottom:14px;box-shadow:0 1px 4px rgba(0,0,0,.06);border:1px solid #e8ebed}
.panel h2{font-size:15px;margin-bottom:12px;color:#1e2a3a;font-weight:600;border-bottom:1px solid #ecf0f1;padding-bottom:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.fg{display:flex;flex-direction:column}
.fg label{font-size:10px;font-weight:600;color:#7f8c8d;margin-bottom:3px;text-transform:uppercase;letter-spacing:.3px}
.fg input,.fg select{padding:7px 10px;border:1px solid #dce1e4;border-radius:4px;font-size:13px;background:#fff}
.fg input:focus,.fg select:focus{outline:none;border-color:#2980b9;box-shadow:0 0 0 2px rgba(41,128,185,.12)}
table{width:100%;border-collapse:collapse;font-size:11.5px}
th{background:#2c3e50;color:#ecf0f1;padding:9px 10px;text-align:left;font-weight:500;white-space:nowrap;position:sticky;top:0;z-index:1;font-size:11px;letter-spacing:.2px}
td{padding:7px 10px;border-bottom:1px solid #ecf0f1;color:#34495e}
tr:hover{background:#edf2f7}
tr:nth-child(even){background:#f8f9fa}
.badge{display:inline-block;padding:3px 8px;border-radius:3px;font-size:10px;font-weight:600}
.badge-ok{background:#d4efdf;color:#1e8449;border:1px solid #a9dfbf}
.badge-err{background:#fadbd8;color:#922b21;border:1px solid #f5b7b1}
.btn{padding:8px 16px;border:none;border-radius:4px;font-size:12px;font-weight:600;cursor:pointer;transition:all .15s}
.btn:hover{opacity:.9}
.btn-p{background:#e67e22;color:#fff}.btn-p:hover{background:#d35400}
.btn-s{background:#ecf0f1;color:#2c3e50;border:1px solid #bdc3c7}.btn-s:hover{background:#d5dbdb}
.btn-d{background:#c0392b;color:#fff;font-size:11px;padding:5px 10px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:18px}
.stat{background:#fff;border-radius:6px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.06);text-align:center;border:1px solid #e8ebed;border-top:3px solid #2980b9}
.stat .v{font-size:24px;font-weight:700;color:#2c3e50}
.stat .l{font-size:10px;color:#7f8c8d;text-transform:uppercase;margin-top:4px;font-weight:600;letter-spacing:.3px}
.alert{padding:10px 14px;border-radius:4px;margin-bottom:12px;font-size:12px}
.alert-ok{background:#d4efdf;border-left:3px solid #27ae60}
.alert-warn{background:#fef9e7;border-left:3px solid #f39c12}
.alert-err{background:#fdedec;border-left:3px solid #e74c3c}
.overflow{overflow-x:auto;max-height:550px;overflow-y:auto;border:1px solid #dce1e4;border-radius:4px}
.actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
.hidden{display:none}
</style>
</head>
<body>
<div class="header">
<div><h1>💰 GB Wage Card Management System</h1><div class="subtitle">Upload Minimum Wage → Auto-Calculate All Components → Download Complete Wage Card</div></div>
<span style="font-size:11px;color:#ccc">Developed by Ravi Kumar (Kmarnuz) | Sr. SME CTK MHLS</span>
</div>
<div class="main">

<!-- UPLOAD SECTION - compact -->
<div class="panel" style="padding:12px 20px;display:flex;align-items:center;justify-content:space-between">
<div style="display:flex;align-items:center;gap:12px">
<button class="btn btn-s" onclick="document.getElementById('upload-file').click()" style="font-size:12px;padding:6px 12px">📤 Full Template</button>
<button class="btn btn-s" onclick="document.getElementById('revision-file').click()" style="font-size:12px;padding:6px 12px;background:#fff8e1;border:1px solid #ff9900">🔄 MW Revision</button>
<a href="/api/revision-template/download" class="btn btn-s" style="font-size:11px;padding:5px 10px;text-decoration:none;color:#545b64">📋 Template</a>
<span id="upload-status" style="font-size:12px"></span>
</div>
<input type="file" id="upload-file" accept=".xlsx,.xls" style="display:none" onchange="uploadFile(this,'full')">
<input type="file" id="revision-file" accept=".xlsx,.xls" style="display:none" onchange="uploadFile(this,'revision')">
<span style="font-size:11px;color:#888">📤 Full: Replace all | 🔄 Revision: Update MW only | <a href="#" onclick="changePassword()" style="color:#545b64">🔒 Change Password</a></span>
</div>

<!-- STATS -->
<div class="stats" id="stats-row"></div>

<!-- DASHBOARD WITH FILTERS -->
<div class="panel">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
<h2>📋 Wage Cards</h2>
<div class="actions">
<button class="btn btn-p" onclick="exportExcel()">📥 Download Complete Wage Card</button>
<button class="btn btn-s" onclick="exportTemplate()" style="border:1px solid #2980b9;color:#2980b9">📥 Updated Template</button>
<button class="btn btn-s" onclick="exportAlfa()" style="background:#e8f5e9;border:1px solid #4caf50">📥 ALFA Rate Card</button>
<button class="btn btn-s" onclick="clearAll()">🗑️ Clear All</button>
</div>
</div>

<!-- Filters -->
<div class="grid" style="margin-bottom:14px">
<div class="fg"><label>Entity</label><select id="f-entity" onchange="loadCards()"><option value="">All Entities</option></select></div>
<div class="fg"><label>State</label><select id="f-state" onchange="loadCards()"><option value="">All States</option></select></div>
<div class="fg"><label>City</label><input id="f-city" placeholder="All Cities" onchange="loadCards()"></div>
<div class="fg"><label>Site Code</label><select id="f-site" onchange="loadCards()"><option value="">All Sites</option></select></div>
<div class="fg"><label>Role</label><select id="f-role" onchange="loadCards()"><option value="">All Roles</option></select></div>
<div class="fg"><label>Tenure</label><select id="f-tenure" onchange="loadCards()"><option value="">All Years</option><option value="0">0 Yr</option><option value="1">1 Yr</option><option value="2">2 Yr</option><option value="3">3 Yr</option><option value="4">4 Yr</option></select></div>
</div>

<!-- Table -->
<div class="overflow">
<table>
<thead><tr>
<th>State</th><th>City</th><th>Role</th><th>Sites</th><th>Tenure</th><th>MW</th>
<th>Basic</th><th>Flexi</th><th>LTA</th><th>HRA</th><th>Conv</th><th>Gross</th>
<th>OT/Hr</th><th>PF(EE)</th><th>ESIC(EE)</th><th>Deductions</th><th>Net</th>
<th>PF(ER)</th><th>ESIC(ER)</th><th>CTC</th><th>MW✓</th><th>50%Cap</th>
</tr></thead>
<tbody id="cards-body"></tbody>
</table>
</div>
<div id="no-data" style="text-align:center;padding:40px;color:#545b64;display:none">
<div style="font-size:36px;margin-bottom:8px">📂</div>
<p>No wage cards yet. Upload a Rate Card to get started.</p>
</div>
</div>

<!-- AUDIT TRAIL -->
<div class="panel" style="padding:12px 20px">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
<span style="font-size:13px;font-weight:600;color:#232f3e">📝 Upload History</span>
</div>
<div class="overflow" style="max-height:200px">
<table>
<thead><tr><th>Date & Time</th><th>Type</th><th>File</th><th>Details</th><th>Download</th></tr></thead>
<tbody id="audit-body"></tbody>
</table>
</div>
<div id="no-audit" style="text-align:center;padding:10px;color:#888;font-size:12px;display:none">No uploads yet</div>
</div>

<!-- LOGIC BUTTON -->
<div style="text-align:right;margin-bottom:8px">
<a href="/api/ptax-depository/download" class="btn btn-s" style="text-decoration:none;font-size:11px;padding:5px 10px;margin-right:6px">📊 P-TAX Depository</a>
<a href="/api/audit-trail/download/ALFA_PTAX_Depository_SlotWise.xlsx" class="btn btn-s" style="text-decoration:none;font-size:11px;padding:5px 10px;margin-right:6px">📊 ALFA P-TAX</a>
<button class="btn btn-s" onclick="uploadPtax()" style="font-size:11px;padding:5px 10px;margin-right:6px">📤 Update P-TAX</button>
<button class="btn btn-s" onclick="toggleLogic()" style="font-size:11px;padding:5px 10px">📖 Logic Depository</button>
<a href="/api/ai-depository/download" class="btn btn-s" style="text-decoration:none;font-size:11px;padding:5px 10px;margin-left:6px;background:#e8f5e9;border:1px solid #4caf50">📋 AI Depository</a>
<button class="btn btn-s" onclick="uploadAiDep()" style="font-size:11px;padding:5px 10px;margin-left:6px;background:#fff3e0;border:1px solid #ff9800">📤 Update AI Depository</button>
<input type="file" id="ptax-file" accept=".xlsx,.xlsb" style="display:none" onchange="submitPtax(this)">
<input type="file" id="ai-dep-file" accept=".xlsx" style="display:none" onchange="submitAiDep(this)">
</div>

<!-- LOGIC DEPOSITORY (hidden by default) -->
<div id="logic-panel" class="panel hidden">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
<h2>📖 Logic Depository</h2>
<a href="/api/logic-depository/download" class="btn btn-s" style="text-decoration:none;font-size:12px">⬇️ Download</a>
</div>
<pre id="logic-content" style="background:#f9fafb;padding:16px;border-radius:6px;font-size:12px;line-height:1.6;overflow-x:auto;white-space:pre-wrap;max-height:500px;overflow-y:auto"></pre>
</div>

</div>

<script>
const fmt=(n)=>n==null||n===undefined?'—':Number(n).toLocaleString('en-IN',{maximumFractionDigits:2});
const fmtN=(n)=>n==null?'—':Number(n).toLocaleString('en-IN',{maximumFractionDigits:0});

let allCards=[];

async function uploadFile(input,mode){
  const file=input.files[0];if(!file)return;
  const pwd=prompt('Enter upload password:');
  if(!pwd){input.value='';return;}
  const status=document.getElementById('upload-status');
  status.innerHTML='<span style="color:#ff9900">⏳ Processing...</span>';
  const formData=new FormData();
  formData.append('file',file);
  formData.append('password',pwd);
  const url=mode==='revision'?'/api/upload-revision':'/api/upload-wage-cards';
  try{
    const r=await fetch(url,{method:'POST',body:formData});
    const d=await r.json();
    if(r.ok){
      const msg=mode==='revision'?`🔄 ${d.cards_updated} cards updated (MW revision)`:`✅ ${d.imported} cards imported`;
      status.innerHTML=`<span style="color:#1e7e34">${msg}</span>`;
      loadCards();
      loadAudit();
    }else{
      status.innerHTML=`<span style="color:#c0392b">❌ ${d.detail||'Failed'}</span>`;
    }
  }catch(e){status.innerHTML=`<span style="color:#c0392b">❌ ${e.message}</span>`;}
  input.value='';
}

async function loadCards(){
  let url='/api/wage-cards?';
  const entity=document.getElementById('f-entity').value;
  const st=document.getElementById('f-state').value;
  const city=document.getElementById('f-city').value;
  const site=document.getElementById('f-site').value;
  const role=document.getElementById('f-role').value;
  const tenure=document.getElementById('f-tenure').value;
  if(st)url+=`state=${st}&`;
  if(role)url+=`business_title=${role}&`;
  if(tenure!=='')url+=`tenure_years=${tenure}&`;

  const r=await fetch(url).then(r=>r.json());
  allCards=r.items||[];

  // Apply client-side filters
  let cards=allCards;
  if(city)cards=cards.filter(c=>c.city.toUpperCase().includes(city.toUpperCase()));
  if(entity)cards=cards.filter(c=>c.entity&&c.entity.toUpperCase()===entity.toUpperCase());
  if(site)cards=cards.filter(c=>c.site_codes&&c.site_codes.toUpperCase()===site.toUpperCase());

  // Sort by state, city, role, tenure
  cards.sort((a,b)=>a.state.localeCompare(b.state)||a.city.localeCompare(b.city)||a.short_bt.localeCompare(b.short_bt)||(a.tenure_years-b.tenure_years));

  // Update stats
  const nonPT=cards.filter(c=>c.mw_compliant!=='N/A');const mwComp=nonPT.filter(c=>c.mw_compliant===true).length;
  const capMet=cards.filter(c=>c.cap_50_met).length;
  const states=[...new Set(cards.map(c=>c.state))].length;
  const cities=[...new Set(cards.map(c=>c.city))].length;
  const sites=[...new Set(cards.map(c=>c.site_codes))].length;
  document.getElementById('stats-row').innerHTML=`
    <div class="stat"><div class="v">${sites}</div><div class="l">Total Sites</div></div>
    <div class="stat"><div class="v">${states}</div><div class="l">States</div></div>
    <div class="stat"><div class="v">${cities}</div><div class="l">Cities</div></div>
    <div class="stat"><div class="v" style="color:${mwComp>=nonPT.length*0.99?'#1e7e34':'#f44336'}">${mwComp}/${nonPT.length}</div><div class="l">MW Compliant</div></div>
`;

  // Update filters (populate dropdowns)
  updateFilters(r.items||[]);

  // Render table
  const tb=document.getElementById('cards-body');
  document.getElementById('no-data').style.display=cards.length===0?'block':'none';

  tb.innerHTML=cards.map(c=>`<tr>
    <td>${c.state}</td><td>${c.city}</td><td>${c.short_bt}</td><td style="font-size:11px">${c.site_codes}</td>
    <td><strong>${c.tenure_years}Yr</strong></td><td>${fmtN(c.minimum_wage)}</td>
    <td>${fmtN(c.basic)}</td><td>${fmtN(c.flexi)}</td><td>${fmtN(c.lta)}</td><td>${fmtN(c.hra)}</td><td>${fmtN(c.conveyance)}</td>
    <td><strong>${fmtN(c.gross)}</strong></td>
    <td>${fmtN(c.per_hour_ot_total)}</td><td>${fmtN(c.pf_employee)}</td><td>${fmtN(c.esic_employee)}</td>
    <td>${fmtN(c.gross_deductions)}</td><td style="color:#1e7e34;font-weight:600">${fmtN(c.net_salary)}</td>
    <td>${fmtN(c.pf_employer)}</td><td>${fmtN(c.esic_employer)}</td>
    <td><strong>${fmtN(c.ctc)}</strong></td>
    <td><span class="badge ${c.mw_compliant==='N/A'?'':c.mw_compliant?'badge-ok':'badge-err'}">${c.mw_compliant==='N/A'?'N/A':c.mw_compliant?'Met':'Gap'}</span></td>
    <td><span class="badge ${c.cap_50_met?'badge-ok':'badge-err'}">${c.cap_50_met?'Met':'Fail'}</span></td>
  </tr>`).join('');
}

function updateFilters(cards){
  const entSel=document.getElementById('f-entity');
  const stSel=document.getElementById('f-state');
  const siteSel=document.getElementById('f-site');
  const roleSel=document.getElementById('f-role');
  const curEnt=entSel.value;
  const curSt=stSel.value;
  const curSite=siteSel.value;
  const curRole=roleSel.value;

  const entities=[...new Set(cards.map(c=>c.entity).filter(Boolean))].sort();
  const states=[...new Set(cards.map(c=>c.state))].sort();
  const sites=[...new Set(cards.map(c=>c.site_codes).filter(Boolean))].sort();
  const roles=[...new Set(cards.map(c=>c.business_title))].sort();

  entSel.innerHTML='<option value="">All Entities</option>'+entities.map(e=>`<option ${e===curEnt?'selected':''}>${e}</option>`).join('');
  stSel.innerHTML='<option value="">All States</option>'+states.map(s=>`<option ${s===curSt?'selected':''}>${s}</option>`).join('');
  siteSel.innerHTML='<option value="">All Sites</option>'+sites.map(s=>`<option ${s===curSite?'selected':''}>${s}</option>`).join('');
  roleSel.innerHTML='<option value="">All Roles</option>'+roles.map(r=>`<option ${r===curRole?'selected':''}>${r}</option>`).join('');
}

async function exportExcel(){
  const st=document.getElementById('f-state').value;
  const url='/api/wage-cards/export/excel'+(st?`?state=${st}`:'');
  const r=await fetch(url);
  if(!r.ok){alert('No cards to export. Upload a Rate Card first.');return;}
  const blob=await r.blob();
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download=`WageCard_Complete_${st||'All'}_${new Date().toISOString().slice(0,10)}.xlsx`;
  a.click();
}

async function exportAlfa(){
  const r=await fetch('/api/alfa-rate-card/export');
  if(!r.ok){alert('No Associate 0-Year cards found. Upload main template first.');return;}
  const blob=await r.blob();
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download=`ALFA_Rate_Card_${new Date().toISOString().slice(0,10)}.xlsx`;
  a.click();
}

async function exportTemplate(){
  const r=await fetch('/api/export-template');
  if(!r.ok){alert('No data to export.');return;}
  const blob=await r.blob();
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download=`Template_Updated_${new Date().toISOString().slice(0,10)}.xlsx`;
  a.click();
}

async function clearAll(){
  const pwd=prompt('Enter password to clear all data:');
  if(!pwd)return;
  if(!confirm('⚠️ This will DELETE all wage cards. Are you sure?'))return;
  const formData=new FormData();
  formData.append('password',pwd);
  const r=await fetch('/api/wage-cards/clear-all',{method:'DELETE',body:formData});
  const d=await r.json();
  if(r.ok){loadCards();loadAudit();}
  else{alert('❌ '+d.detail);}
}

// Load on start
loadCards();
loadAudit();

async function changePassword(){
  const cur=prompt('Enter current password:');
  if(!cur)return;
  const newp=prompt('Enter new password (min 4 chars):');
  if(!newp)return;
  const formData=new FormData();
  formData.append('current_password',cur);
  formData.append('new_password',newp);
  const r=await fetch('/api/change-password',{method:'POST',body:formData});
  const d=await r.json();
  if(r.ok){alert('✅ Password changed successfully!');}
  else{alert('❌ '+d.detail);}
}

async function loadAudit(){
  const r=await fetch('/api/audit-trail').then(r=>r.json());
  const entries=(r.entries||[]).filter(e=>e.action==='UPLOAD'||e.action==='MW_REVISION');
  document.getElementById('no-audit').style.display=entries.length===0?'block':'none';
  document.getElementById('audit-body').innerHTML=entries.map(e=>{
    const dt=new Date(e.timestamp+'Z').toLocaleString('en-IN');
    const type=e.action==='MW_REVISION'?'🔄 MW Revision':'📤 Full Template';
    const dl=`<a href="/api/audit-trail/download/${e.filename}" style="text-decoration:none;font-size:11px">⬇️ Download</a>`;
    return `<tr><td style="font-size:11px">${dt}</td><td style="font-size:11px">${type}</td><td style="font-size:11px">${e.filename}</td><td style="font-size:11px">${e.details}</td><td>${dl}</td></tr>`;
  }).join('');
}

let logicLoaded=false;
async function toggleLogic(){
  const panel=document.getElementById('logic-panel');
  panel.classList.toggle('hidden');
  if(!logicLoaded){
    const r=await fetch('/api/logic-depository').then(r=>r.json());
    document.getElementById('logic-content').textContent=r.content;
    logicLoaded=true;
  }
}

function uploadPtax(){
  const pwd=prompt('Enter password to update P-TAX:');
  if(!pwd)return;
  window._ptaxPwd=pwd;
  document.getElementById('ptax-file').click();
}
async function submitPtax(input){
  const file=input.files[0];if(!file)return;
  const formData=new FormData();
  formData.append('file',file);
  formData.append('password',window._ptaxPwd||'');
  const r=await fetch('/api/ptax-depository/upload',{method:'POST',body:formData});
  const d=await r.json();
  if(r.ok){alert('✅ P-TAX updated: '+d.states_updated+' states');}
  else{alert('❌ '+d.detail);}
  input.value='';
}
function uploadAiDep(){
  const pwd=prompt('Enter password to update AI Depository:');
  if(!pwd)return;
  window._aiDepPwd=pwd;
  document.getElementById('ai-dep-file').click();
}
async function submitAiDep(input){
  const file=input.files[0];if(!file)return;
  const formData=new FormData();
  formData.append('file',file);
  formData.append('password',window._aiDepPwd||'');
  const r=await fetch('/api/ai-depository/upload',{method:'POST',body:formData});
  const d=await r.json();
  if(r.ok){alert('✅ AI Depository updated: '+d.entries+' entries, '+d.cards_updated+' cards updated');}
  else{alert('❌ '+(d.detail||'Upload failed'));}
  input.value='';
  loadData();
}
</script>
</body></html>"""
