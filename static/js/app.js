/* ShoutCode — frontend logic */

const form        = document.getElementById("smsForm");
const phoneInput  = document.getElementById("phone");
const carrierFld  = document.getElementById("carrierField");
const carrierSel  = document.getElementById("carrier");
const msgInput    = document.getElementById("message");
const charCount   = document.getElementById("charCount");
const sendBtn     = document.getElementById("sendBtn");
const btnText     = document.getElementById("btnText");
const btnSpinner  = document.getElementById("btnSpinner");
const resultDiv   = document.getElementById("result");
const tabs        = document.querySelectorAll(".tab");

let currentMethod = "gateway";

// ── Tabs ────────────────────────────────────────────────
tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    tabs.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    currentMethod = tab.dataset.method;

    if (currentMethod === "gateway") {
      carrierFld.style.display = "";
      carrierSel.required = true;
    } else {
      carrierFld.style.display = "none";
      carrierSel.required = false;
    }

    clearResult();
  });
});

// ── Char Counter ────────────────────────────────────────
msgInput.addEventListener("input", () => {
  const len = msgInput.value.length;
  charCount.textContent = `${len} / 160`;
  charCount.style.color = len > 140 ? (len === 160 ? "#ef4444" : "#f97316") : "";
});

// ── Form Submit ─────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearResult();
  setLoading(true);

  const payload = {
    phone:   phoneInput.value.trim(),
    message: msgInput.value.trim(),
    method:  currentMethod,
    carrier: currentMethod === "gateway" ? carrierSel.value : "",
  };

  try {
    const res  = await fetch("/send", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.success) {
      let detail = "";
      if (data.method === "email-gateway") detail = ` via ${data.gateway}`;
      if (data.method === "textbelt" && data.quotaRemaining !== undefined)
        detail = ` · ${data.quotaRemaining} free sends left today`;
      showResult("success", `✅ Message sent${detail}`);
      form.reset();
      charCount.textContent = "0 / 160";
    } else {
      showResult("error", `❌ ${data.error || "Send failed. Check your settings."}`);
    }
  } catch (err) {
    showResult("error", "❌ Network error — is the server running?");
  } finally {
    setLoading(false);
  }
});

// ── Helpers ─────────────────────────────────────────────
function setLoading(on) {
  sendBtn.disabled = on;
  btnText.textContent = on ? "Sending…" : "Send Message";
  btnSpinner.classList.toggle("hidden", !on);
}

function showResult(type, msg) {
  resultDiv.className = `result ${type}`;
  resultDiv.textContent = msg;
  resultDiv.classList.remove("hidden");
}

function clearResult() {
  resultDiv.className = "result hidden";
  resultDiv.textContent = "";
}
