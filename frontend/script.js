const API_BASE = "";  // Same origin (FastAPI serves frontend)

let sessionId = localStorage.getItem("sessionId");

// Init session
(async () => {
  if (!sessionId) {
    await startNewSession();
  }
})();

async function startNewSession() {
  try {
    const res = await fetch(`${API_BASE}/api/session/new`);
    const data = await res.json();
    sessionId = data.sessionId;
    localStorage.setItem("sessionId", sessionId);
    clearMessages();
  } catch (e) {
    console.error("Failed to create session:", e);
  }
}

function clearMessages() {
  const msgArea = document.getElementById("messages");
  msgArea.innerHTML = `
    <div class="welcome">
      <div class="welcome-icon">✦</div>
      <h2>How can I help you today?</h2>
      <p>Ask me anything about your account, billing, security, or settings.</p>
    </div>`;
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 140) + "px";
}

function sendQuickQ(question) {
  const input = document.getElementById("userInput");
  input.value = question;
  sendMessage();
}

async function sendMessage() {
  const input = document.getElementById("userInput");
  const message = input.value.trim();
  if (!message) return;

  appendMessage("user", message);
  input.value = "";
  input.style.height = "auto";

  const sendBtn = document.getElementById("sendBtn");
  sendBtn.disabled = true;

  const typingId = appendTyping();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, message })
    });

    removeTyping(typingId);

    if (!res.ok) {
      const err = await res.json();
      appendBotMessage("⚠️ " + (err.detail || "Something went wrong."), 0, false);
    } else {
      const data = await res.json();
      appendBotMessage(data.reply, data.retrievedChunks, data.grounded);
    }
  } catch (e) {
    removeTyping(typingId);
    appendBotMessage("⚠️ Could not reach the server. Please try again.", 0, false);
  }

  sendBtn.disabled = false;
  scrollToBottom();
}

function appendMessage(role, text) {
  const msgArea = document.getElementById("messages");

  // Remove welcome if present
  const welcome = msgArea.querySelector(".welcome");
  if (welcome) welcome.remove();

  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `
    <div class="avatar">${role === "user" ? "U" : "✦"}</div>
    <div class="bubble">${escapeHtml(text)}</div>`;
  msgArea.appendChild(div);
  scrollToBottom();
}

function appendBotMessage(text, chunks, grounded) {
  const msgArea = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = "msg bot";

  const badge = grounded
    ? `<span class="grounded-badge">✓ ${chunks} source${chunks !== 1 ? "s" : ""}</span>`
    : `<span style="color:var(--text-muted)">No sources matched</span>`;

  div.innerHTML = `
    <div class="avatar">✦</div>
    <div>
      <div class="bubble">${escapeHtml(text)}</div>
      <div class="bubble-meta">${badge}</div>
    </div>`;
  msgArea.appendChild(div);
  scrollToBottom();
}

let typingCounter = 0;
function appendTyping() {
  const id = `typing-${typingCounter++}`;
  const msgArea = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = "msg bot";
  div.id = id;
  div.innerHTML = `
    <div class="avatar">✦</div>
    <div class="bubble">
      <div class="typing"><span></span><span></span><span></span></div>
    </div>`;
  msgArea.appendChild(div);
  scrollToBottom();
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollToBottom() {
  const msgArea = document.getElementById("messages");
  msgArea.scrollTop = msgArea.scrollHeight;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\n/g, "<br>");
}
