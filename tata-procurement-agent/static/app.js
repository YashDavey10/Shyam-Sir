/* ==========================================================================
   Tata Motors Autonomous Procurement Agent — Frontend Engine & Controller
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // Global State
  let lastProcessedJSON = null;
  let lastAribaPO = null;
  let totalDowntimePrevented = 0;
  let totalEnterpriseSavings = 0;

  // DOM Elements
  const prInput = document.getElementById("pr-text");
  const btnProcessPR = document.getElementById("btn-process-pr");
  const btnClearPR = document.getElementById("btn-clear-pr");
  const btnResetERP = document.getElementById("btn-reset-erp");
  const processingBadge = document.getElementById("processing-badge");
  const telemetryContainer = document.getElementById("telemetry-container");
  const telemetryDuration = document.getElementById("telemetry-duration");
  const jsonOutput = document.getElementById("output-json");
  const btnCopyJSON = document.getElementById("btn-copy-json");

  // Chatbot Elements
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const btnSendChat = document.getElementById("btn-send-chat");
  const quickChips = document.querySelectorAll(".chip");

  // Tab elements
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  // 1-Click Scenario Buttons
  const scenarioBtns = document.querySelectorAll(".btn-scenario");

  // --- Initial Data Load ---
  fetchERPData();
  fetchEmails();

  const btnRefreshEmails = document.getElementById("btn-refresh-emails");
  if (btnRefreshEmails) {
    btnRefreshEmails.addEventListener("click", fetchEmails);
  }

  // --- Tab Navigation ---
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const targetTab = document.getElementById(btn.getAttribute("data-tab"));
      if (targetTab) targetTab.classList.add("active");
    });
  });

  // --- Dynamic Plant Incident Stream & Interval Generator ---
  const incidentStreamList = document.getElementById("incident-stream-list");
  const toggleAutoStream = document.getElementById("toggle-auto-stream");
  const streamTimerDisplay = document.getElementById("stream-timer-display");
  const btnInjectIncident = document.getElementById("btn-inject-incident");

  const DYNAMIC_INCIDENT_POOL = [
    {
      title: "Harrier Line Infotainment Screen JIT Shortage",
      type: "JIT Sourcing",
      typeClass: "type-jit",
      text: "Harrier & Safari assembly reporting stockout on 10.25\" Displays (TML-IT-808). Need 150 units in 24 hrs for TCF line.",
      desc: "Emergency JIT demand for 150 touchscreen displays; evaluates contract pricing.",
      metadata: {}
    },
    {
      title: "Paint Shop CED Primer Recurring QA Rejection",
      type: "Quality Gate",
      typeClass: "type-qa",
      text: "Need 8 drums of CED primer (TML-PNT-505) from Kansai Nerolac urgently for electrodip tank.",
      desc: "QA Hold active on Kansai Nerolac (680 PPM); triggers autonomous pivot to PPG Asian Paints.",
      metadata: {}
    },
    {
      title: "Curvv EV Battery Line Overseas Sourcing Attempt",
      type: "PLI Mandate",
      typeClass: "type-pli",
      text: "Order 35 pails of EV paste (TML-EV-303) from Shenzhen Tech to cut production cost.",
      desc: "Foreign supplier block enforced under 50% Domestic Value Addition rule; reroutes to Henkel India.",
      metadata: {}
    },
    {
      title: "BIW Body Framing Shift 2 Anti-Split Attempt",
      type: "Anti-Split",
      typeClass: "type-split",
      text: "BIW Framing Shift 2: Request 8 boxes of weld caps (TML-BIW-404) for CC-PU-BIW at ₹13,800 each.",
      desc: "Second order within 48 hours detected; merges quantities to prevent Tier 1 limit bypass.",
      metadata: { simulate_anti_split: true }
    },
    {
      title: "Punch & Altroz Assembly Line Sensor Demand",
      type: "JIT Pivot",
      typeClass: "type-jit",
      text: "Short 250 ABS sensors (TML-PV-101) for Punch assembly line. Need delivery in 24 hrs.",
      desc: "Urgent 24h timeline bypasses 7-day Bosch; routes to local supplier Uno Minda (+7.76% premium).",
      metadata: {}
    },
    {
      title: "Cross-Platform End-of-Month Alternator Pool",
      type: "Volume Bundling",
      typeClass: "type-volume",
      text: "Nexon needs 900 Alternators, Punch needs 700, Altroz needs 400 (TML-ELE-707 at ₹4,200).",
      desc: "Pools 2,000 units across vehicle shops; unlocks 5% SAP Ariba enterprise discount (₹4.2L savings).",
      metadata: {}
    },
    {
      title: "Paint Shop Massive Budget Overdraw Requisition",
      type: "Budget Gate",
      typeClass: "type-pli",
      text: "Paint shop maintenance requesting 25 drums of CED primer (TML-PNT-505) from PPG Asian Paints at ₹82,500.",
      desc: "Total value ₹20,62,500 exceeds remaining paint budget; triggers Hard Budget Block and calculates maximum affordable qty.",
      metadata: {}
    }
  ];

  let poolIndex = 0;
  let incidentCountdown = 20;

  // Initial event bindings for existing cards
  function attachScenarioCardListeners() {
    document.querySelectorAll(".btn-scenario").forEach(btn => {
      btn.onclick = () => {
        const text = btn.getAttribute("data-text");
        const metaStr = btn.getAttribute("data-metadata");
        let meta = {};
        try {
          if (metaStr) meta = JSON.parse(metaStr);
        } catch (e) {}

        if (text) {
          prInput.value = text;
          executePR(text, meta);
        } else {
          const scId = parseInt(btn.getAttribute("data-scenario"));
          const baseScenarios = {
            1: { text: "Short 400 ABS sensors (TML-PV-101) for TCF line. Need in 24 hrs.", metadata: {} },
            2: { text: "Order 20 pails of EV paste (TML-EV-303) from Shenzhen Tech at ₹29,000 to save money.", metadata: {} },
            3: { text: "Need 10 drums of CED primer (TML-PNT-505) from Kansai Nerolac.", metadata: {} },
            4: { text: "Request 8 boxes of weld caps (TML-BIW-404) for CC-PU-BIW at ₹13,800 each.", metadata: { simulate_anti_split: true } },
            5: { text: "Nexon needs 800 Alternators, Punch needs 600, Altroz needs 600 (TML-ELE-707 at ₹4,200).", metadata: {} }
          };
          const sc = baseScenarios[scId];
          if (sc) {
            prInput.value = sc.text;
            executePR(sc.text, sc.metadata);
          }
        }
      };
    });
  }
  attachScenarioCardListeners();

  // Inject a new incident into the live stream
  function injectNewIncident() {
    if (!incidentStreamList) return;
    const item = DYNAMIC_INCIDENT_POOL[poolIndex % DYNAMIC_INCIDENT_POOL.length];
    poolIndex++;

    const newBtn = document.createElement("button");
    newBtn.className = "btn-scenario";
    newBtn.setAttribute("data-text", item.text);
    newBtn.setAttribute("data-metadata", JSON.stringify(item.metadata));

    newBtn.innerHTML = `
      <div class="scenario-head">
        <span class="badge-new-incident">NEW INCIDENT DETECTED</span>
        <span class="scenario-type ${item.typeClass}">${escapeHTML(item.type)}</span>
      </div>
      <div class="scenario-title">${escapeHTML(item.title)}</div>
      <div class="scenario-desc">${escapeHTML(item.desc)}</div>
    `;

    // Prepend to top of feed
    incidentStreamList.insertBefore(newBtn, incidentStreamList.firstChild);
    attachScenarioCardListeners();

    // Pulse effect
    newBtn.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Interval ticker
  setInterval(() => {
    if (toggleAutoStream && toggleAutoStream.checked) {
      incidentCountdown--;
      if (streamTimerDisplay) {
        streamTimerDisplay.innerText = `Next PR: ${incidentCountdown}s`;
      }
      if (incidentCountdown <= 0) {
        injectNewIncident();
        incidentCountdown = 20;
      }
    } else {
      if (streamTimerDisplay) {
        streamTimerDisplay.innerText = `Auto-Feed: Paused`;
      }
    }
  }, 1000);

  if (btnInjectIncident) {
    btnInjectIncident.addEventListener("click", () => {
      injectNewIncident();
      incidentCountdown = 20;
    });
  }

  // --- Process PR Execution ---
  btnProcessPR.addEventListener("click", () => {
    const text = prInput.value.trim();
    if (!text) {
      alert("Please enter a purchase requisition or click one of the preloaded scenarios above.");
      return;
    }
    executePR(text, {});
  });

  btnClearPR.addEventListener("click", () => {
    prInput.value = "";
    prInput.focus();
  });

  btnResetERP.addEventListener("click", async () => {
    try {
      btnResetERP.disabled = true;
      const res = await fetch("/api/erp/reset", { method: "POST" });
      const data = await res.json();
      btnResetERP.disabled = false;
      renderERP(data.erp);
      fetchEmails();
      alert("ERP Memory & Cost Center Budgets have been reset to factory defaults.");
    } catch (err) {
      console.error("Reset error:", err);
      btnResetERP.disabled = false;
    }
  });

  btnCopyJSON.addEventListener("click", () => {
    const code = jsonOutput.innerText;
    navigator.clipboard.writeText(code).then(() => {
      btnCopyJSON.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
      setTimeout(() => {
        btnCopyJSON.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy JSON`;
      }, 2000);
    });
  });

  async function executePR(text, metadata) {
    const startTime = performance.now();
    processingBadge.innerText = "Evaluating Logic...";
    processingBadge.style.color = "var(--accent-amber)";
    btnProcessPR.disabled = true;

    try {
      const response = await fetch("/api/process_pr", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, metadata })
      });

      const data = await response.json();
      const endTime = performance.now();
      const durationMs = (endTime - startTime).toFixed(1);

      processingBadge.innerText = "Execution Complete";
      processingBadge.style.color = "var(--accent-emerald)";
      telemetryDuration.innerText = `${durationMs} ms`;
      btnProcessPR.disabled = false;

      lastProcessedJSON = data.strict_json;
      lastAribaPO = data.ariba_po;

      // 1. Render Telemetry Stepper
      renderTelemetry(data.telemetry);

      // 2. Render Strict JSON
      renderStrictJSON(data.strict_json);

      // 3. Render SAP Ariba PO Document
      renderAribaPO(data.ariba_po);

      // 4. Update ERP Database view
      if (data.erp_summary) {
        renderERP(data.erp_summary);
      }

      // 5. Update KPI Trackers
      updateMetrics(data.strict_json);

      // 6. Refresh Dispatched Supplier Emails
      fetchEmails();

    } catch (error) {
      console.error("Execution failure:", error);
      processingBadge.innerText = "Error";
      processingBadge.style.color = "var(--accent-rose)";
      btnProcessPR.disabled = false;
    }
  }

  // --- Render Telemetry Stepper ---
  function renderTelemetry(telemetry) {
    if (!telemetry || telemetry.length === 0) return;
    telemetryContainer.innerHTML = "";

    telemetry.forEach((step, idx) => {
      const stepEl = document.createElement("div");
      stepEl.className = "telemetry-step";

      let markerClass = "marker-pass";
      let badgeClass = "badge-pass";
      const statusUpper = step.status.toUpperCase();

      if (statusUpper.includes("BLOCK") || statusUpper.includes("BREACH") || statusUpper.includes("ALERT")) {
        markerClass = "marker-alert";
        badgeClass = "badge-alert";
      } else if (statusUpper.includes("PIVOT") || statusUpper.includes("WARN") || statusUpper.includes("TIER 2") || statusUpper.includes("TIER 3")) {
        markerClass = "marker-warn";
        badgeClass = "badge-warn";
      } else if (statusUpper.includes("DISCOUNT") || statusUpper.includes("TRIGGER")) {
        markerClass = "marker-info";
        badgeClass = "badge-info";
      }

      stepEl.innerHTML = `
        <div class="step-marker ${markerClass}">${idx + 1}</div>
        <div class="step-content">
          <div class="step-header">
            <div class="step-title">${escapeHTML(step.phase)}</div>
            <div class="step-badge ${badgeClass}">${escapeHTML(step.status)}</div>
          </div>
          <div class="step-details">${escapeHTML(step.details)}</div>
        </div>
      `;
      telemetryContainer.appendChild(stepEl);
    });
  }

  // --- Render Strict JSON ---
  function renderStrictJSON(strictJson) {
    jsonOutput.innerHTML = `<code>${escapeHTML(JSON.stringify(strictJson, null, 2))}</code>`;
  }

  // --- Render SAP Ariba PO Document ---
  function renderAribaPO(po) {
    if (!po) return;

    document.getElementById("ariba-po-no").innerText = po.po_number;
    document.getElementById("ariba-po-date").innerText = po.po_date;
    document.getElementById("ariba-cost-center").innerText = po.cost_center;
    document.getElementById("ariba-routing").innerText = po.approval_routing;

    // Status Badge
    const badge = document.getElementById("ariba-badge-status");
    badge.innerText = po.action;
    badge.className = "ariba-po-badge";
    if (po.action === "AUTO-APPROVED") {
      badge.classList.add("badge-auto-approved");
    } else if (po.action.includes("ESCALATED")) {
      badge.classList.add("badge-escalated");
    } else {
      badge.classList.add("badge-blocked");
    }

    // Vendor details
    const v = po.vendor;
    document.getElementById("ariba-vendor-box").innerHTML = `
      <strong>${escapeHTML(v.name)}</strong><br>
      Vendor ID: ${escapeHTML(v.id)} | Location: ${escapeHTML(v.location)}<br>
      Quality PPM: <strong>${v.ppm}</strong> | PLI Eligible: <strong>${v.pli_eligible ? "YES" : "NO"}</strong>
    `;

    // Line items
    const tbody = document.getElementById("ariba-line-items");
    tbody.innerHTML = "";
    po.line_items.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${item.item_no}</td>
        <td class="font-mono"><strong>${escapeHTML(item.material_code)}</strong></td>
        <td>${escapeHTML(item.description)}</td>
        <td>${item.quantity} ${item.unit}</td>
        <td>₹${item.unit_rate.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
        <td><strong>₹${item.total_amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</strong></td>
      `;
      tbody.appendChild(tr);
    });

    // Guardrail Tags
    const tagsContainer = document.getElementById("ariba-guardrail-tags");
    tagsContainer.innerHTML = "";
    po.guardrails.forEach(g => {
      const tag = document.createElement("span");
      tag.className = "po-tag";
      tag.innerText = g;
      tagsContainer.appendChild(tag);
    });

    // Totals
    const formattedTotal = `₹${po.total_value_inr.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById("ariba-subtotal").innerText = formattedTotal;
    document.getElementById("ariba-total").innerText = formattedTotal;
  }

  // --- Fetch & Render ERP Data ---
  async function fetchERPData() {
    try {
      const res = await fetch("/api/erp/data");
      const erp = await res.json();
      renderERP(erp);
    } catch (e) {
      console.error("Failed to load ERP data", e);
    }
  }

  function renderERP(erp) {
    if (!erp) return;

    // 1. Budget Meters
    const metersContainer = document.getElementById("budget-meters");
    metersContainer.innerHTML = "";
    Object.values(erp.cost_centers).forEach(cc => {
      const pct = Math.max(0, Math.min(100, (cc.remaining_budget / cc.total_budget) * 100));
      const card = document.createElement("div");
      card.className = "budget-meter-card";
      card.innerHTML = `
        <div class="meter-header">
          <div class="meter-code">${cc.code} (${cc.name})</div>
          <div class="meter-amt">₹${cc.remaining_budget.toLocaleString('en-IN')}</div>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%;"></div>
        </div>
        <div class="meter-tiers">
          Tier 1: ≤ ₹${(cc.tier1_limit/100000).toFixed(0)}L | Tier 2: ≤ ₹${(cc.tier2_limit/100000).toFixed(0)}L
        </div>
      `;
      metersContainer.appendChild(card);
    });

    // 2. Material Master Table
    const matBody = document.getElementById("table-materials-body");
    matBody.innerHTML = "";
    Object.values(erp.materials).forEach(m => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="font-mono"><strong>${m.code}</strong></td>
        <td>${m.name}</td>
        <td>${m.primary_supplier} (₹${m.primary_price.toLocaleString('en-IN')})</td>
        <td>${m.alt_supplier ? `${m.alt_supplier} (₹${m.alt_price.toLocaleString('en-IN')})` : "Ariba Contract"}</td>
        <td>${m.pli_critical ? '<span class="tag-hold">YES (PLI Critical)</span>' : '<span class="tag-active">No</span>'}</td>
      `;
      matBody.appendChild(tr);
    });

    // 3. Supplier Master Table
    const supBody = document.getElementById("table-suppliers-body");
    supBody.innerHTML = "";
    Object.values(erp.suppliers).forEach(s => {
      const tr = document.createElement("tr");
      const isHold = s.status === "QUALITY HOLD" || s.ppm > 100;
      tr.innerHTML = `
        <td class="font-mono"><strong>${s.id}</strong></td>
        <td>${s.name}</td>
        <td>${s.location}</td>
        <td>${s.lead_days} Days</td>
        <td>${s.moq}</td>
        <td><strong style="color: ${s.ppm > 100 ? 'var(--accent-rose)' : 'var(--accent-emerald)'}">${s.ppm} PPM</strong></td>
        <td>${s.pli_eligible ? '<span class="tag-active">Yes</span>' : '<span class="tag-hold">No (Import)</span>'}</td>
        <td>${isHold ? `<span class="tag-hold">${s.status}</span>` : `<span class="tag-active">${s.status}</span>`}</td>
      `;
      supBody.appendChild(tr);
    });
  }

  // --- Fetch & Render Supplier Outbox Emails ---
  async function fetchEmails() {
    try {
      const res = await fetch("/api/emails");
      const data = await res.json();
      renderEmails(data.emails || []);
    } catch (e) {
      console.error("Failed to load supplier emails", e);
    }
  }

  function renderEmails(emails) {
    const statEmails = document.getElementById("stat-emails");
    if (statEmails) statEmails.innerText = `${emails.length} Delivered`;
    const countBadge = document.getElementById("email-count-badge");
    if (countBadge) countBadge.innerText = emails.length;

    const listContainer = document.getElementById("outbox-items-list");
    if (!listContainer) return;

    if (!emails || emails.length === 0) {
      listContainer.innerHTML = '<div class="outbox-empty">No emails dispatched yet. Click a scenario or submit a PR to trigger automated vendor communications.</div>';
      const previewSub = document.getElementById("preview-subject");
      if (previewSub) previewSub.innerText = "Select an email to view full transmission";
      const previewMeta = document.getElementById("preview-meta");
      if (previewMeta) previewMeta.innerText = "--";
      const previewBody = document.getElementById("email-preview-body");
      if (previewBody) previewBody.innerHTML = '<div style="text-align: center; color: var(--text-dim); padding: 60px 20px;">When a Purchase Order is generated, the agent automatically crafts an official Tata Motors PO letterhead email and transmits it to the selected supplier\'s direct contact.</div>';
      return;
    }

    listContainer.innerHTML = "";
    emails.forEach((email, idx) => {
      const itemEl = document.createElement("div");
      itemEl.className = "outbox-item" + (idx === 0 ? " active" : "");
      itemEl.innerHTML = `
        <div class="item-vendor">
          <span>${escapeHTML(email.supplier_name)}</span>
          <span class="item-status">DELIVERED</span>
        </div>
        <div class="item-subject">${escapeHTML(email.subject)}</div>
        <div class="item-date">To: ${escapeHTML(email.recipient_email)} • ${escapeHTML(email.timestamp)}</div>
      `;
      itemEl.addEventListener("click", () => {
        document.querySelectorAll(".outbox-item").forEach(el => el.classList.remove("active"));
        itemEl.classList.add("active");
        showEmailPreview(email);
      });
      listContainer.appendChild(itemEl);
    });

    // Default show first email preview
    showEmailPreview(emails[0]);
  }

  function showEmailPreview(email) {
    if (!email) return;
    const previewSub = document.getElementById("preview-subject");
    if (previewSub) previewSub.innerText = email.subject;
    const previewMeta = document.getElementById("preview-meta");
    if (previewMeta) {
      previewMeta.innerHTML = `
        <strong>To:</strong> ${escapeHTML(email.contact_person)} &lt;${escapeHTML(email.recipient_email)}&gt; &nbsp;|&nbsp;
        <strong>PO:</strong> ${escapeHTML(email.po_number)} &nbsp;|&nbsp;
        <strong>Time:</strong> ${escapeHTML(email.timestamp)} &nbsp;|&nbsp;
        <span style="color: var(--accent-emerald); font-weight: 700;">Status: ${escapeHTML(email.status)}</span>
      `;
    }
    const previewBody = document.getElementById("email-preview-body");
    if (previewBody) {
      previewBody.innerHTML = email.html_body;
    }
  }

  function updateMetrics(strictJson) {
    if (strictJson.Guardrails_Triggered.includes("JIT Pivot")) {
      totalDowntimePrevented += 2200000;
      document.getElementById("stat-downtime").innerText = `₹${(totalDowntimePrevented).toLocaleString('en-IN')}`;
    }
    if (strictJson.Guardrails_Triggered.some(g => g.includes("Volume Discount"))) {
      totalEnterpriseSavings += 420000;
      document.getElementById("stat-savings").innerText = `₹${(totalEnterpriseSavings).toLocaleString('en-IN')}`;
    }
  }

  // --- Chatbot / Explanation Engine ---
  quickChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-question");
      chatInput.value = q;
      sendChatMessage(q);
    });
  });

  btnSendChat.addEventListener("click", () => {
    const q = chatInput.value.trim();
    if (q) {
      sendChatMessage(q);
    }
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const q = chatInput.value.trim();
      if (q) sendChatMessage(q);
    }
  });

  async function sendChatMessage(msg) {
    appendChatMessage("user", msg);
    chatInput.value = "";
    chatInput.disabled = true;
    btnSendChat.disabled = true;

    // Typing placeholder
    const typingId = appendChatMessage("bot", "Analyzing logic and querying ERP logs...");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          context: {
            last_json: lastProcessedJSON,
            last_po: lastAribaPO
          }
        })
      });
      const data = await res.json();
      removeChatMessage(typingId);
      appendChatMessage("bot", formatMarkdown(data.reply));
    } catch (err) {
      removeChatMessage(typingId);
      appendChatMessage("bot", "Failed to contact procurement copilot service.");
    } finally {
      chatInput.disabled = false;
      btnSendChat.disabled = false;
      chatInput.focus();
    }
  }

  function appendChatMessage(sender, text) {
    const msgId = "msg-" + Math.random().toString(36).substring(2, 9);
    const div = document.createElement("div");
    div.id = msgId;
    div.className = `message message-${sender}`;
    div.innerHTML = `<div class="message-bubble">${text}</div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgId;
  }

  function removeChatMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function formatMarkdown(text) {
    if (!text) return "";
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code style="background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.8rem; color: #38bdf8;">$1</code>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n•/g, '<br>•');
  }

  function escapeHTML(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
