"""
Zubhai Frontend Patch Script
Applies all 7 feature additions to index.html
Run: python3 patch_frontend.py index.html
"""
import sys, re

def patch(content: str) -> str:

    # ═══════════════════════════════════════════════════════════════════
    # 1. ADD CSS for milestone popup, OTP flow, feedback modal, copy btn
    # ═══════════════════════════════════════════════════════════════════
    new_css = """
/* ── MILESTONE CELEBRATION ───────────────────────────── */
.milestone-overlay{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:1000;display:none;align-items:center;justify-content:center;padding:24px;backdrop-filter:blur(6px)}
.milestone-overlay.show{display:flex}
.milestone-modal{background:#fff;border-radius:20px;padding:40px 36px;max-width:420px;width:100%;text-align:center;position:relative;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,.3)}
.milestone-modal::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:var(--milestone-color,var(--accent));border-radius:20px 20px 0 0}
.milestone-emoji{font-size:56px;display:block;margin-bottom:14px;animation:bounceIn .6s cubic-bezier(.68,-.55,.27,1.55)}
.milestone-title{font-family:var(--fs);font-size:28px;color:var(--text);font-weight:400;letter-spacing:-.5px;margin-bottom:6px}
.milestone-sub{font-size:13px;color:var(--text2);margin-bottom:16px}
.milestone-body{font-size:14px;color:var(--text2);line-height:1.85;background:var(--bg2);border:1px solid var(--border);border-radius:var(--r8);padding:14px;margin-bottom:18px;text-align:left}
.milestone-cta-text{font-size:13px;color:var(--accent2);margin-bottom:18px;font-weight:500}
.milestone-close-btn{width:100%;background:var(--text);color:#fff;border:none;border-radius:var(--r8);padding:13px;font-size:14px;font-weight:500;font-family:var(--fb);cursor:pointer;transition:.2s}
.milestone-close-btn:hover{background:#333}
@keyframes bounceIn{0%{transform:scale(0);opacity:0}60%{transform:scale(1.2)}100%{transform:scale(1);opacity:1}}
/* confetti particles */
.confetti-piece{position:absolute;width:8px;height:8px;border-radius:2px;animation:confettiFall 3s linear forwards;pointer-events:none}
@keyframes confettiFall{0%{transform:translateY(-20px) rotate(0deg);opacity:1}100%{transform:translateY(500px) rotate(720deg);opacity:0}}

/* ── OTP AUTH FLOW ───────────────────────────────────── */
.otp-step{display:none}.otp-step.show{display:block}
.otp-digits{display:flex;gap:8px;justify-content:center;margin-bottom:14px}
.otp-digit{width:44px;height:52px;text-align:center;font-size:22px;font-family:var(--fm);border:1.5px solid var(--border2);border-radius:var(--r8);background:#fff;color:var(--text);transition:.2s}
.otp-digit:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(232,96,44,.1)}
.otp-resend{font-size:11px;color:var(--text3);text-align:center;margin-top:8px;cursor:pointer;transition:.2s}
.otp-resend:hover{color:var(--text2)}
.otp-resend.disabled{pointer-events:none;opacity:.4}
.otp-email-display{font-size:13px;color:var(--text2);text-align:center;margin-bottom:16px}
.otp-email-display strong{color:var(--text)}

/* ── FEEDBACK MODAL ──────────────────────────────────── */
.feedback-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:900;display:none;align-items:center;justify-content:center;padding:24px;backdrop-filter:blur(4px)}
.feedback-overlay.show{display:flex}
.feedback-modal{background:#fff;border:1px solid var(--border);border-radius:var(--r16);padding:28px;max-width:400px;width:100%;box-shadow:0 12px 48px rgba(0,0,0,.15)}
.feedback-modal h3{font-family:var(--fs);font-size:22px;font-weight:400;color:var(--text);margin-bottom:6px;letter-spacing:-.3px}
.feedback-modal p{font-size:13px;color:var(--text3);margin-bottom:16px}
.feedback-type-row{display:flex;gap:6px;margin-bottom:12px}
.feedback-type-btn{flex:1;padding:8px;border:1px solid var(--border2);border-radius:var(--r6);font-size:11px;font-family:var(--fb);cursor:pointer;background:none;color:var(--text2);transition:.15s;text-align:center}
.feedback-type-btn:hover,.feedback-type-btn.on{border-color:var(--accent);color:var(--accent);background:rgba(232,96,44,.06)}
.feedback-ta{width:100%;background:var(--bg2);border:1px solid var(--border2);border-radius:var(--r8);padding:10px 12px;color:var(--text);font-size:13px;font-family:var(--fb);height:90px;resize:none;margin-bottom:10px}
.feedback-ta:focus{outline:none;border-color:var(--border3)}
.feedback-send-btn{width:100%;background:var(--accent);color:#fff;border:none;border-radius:var(--r8);padding:12px;font-size:13px;font-weight:500;font-family:var(--fb);cursor:pointer;transition:.2s}
.feedback-send-btn:hover{background:var(--accent2)}
.feedback-cancel{width:100%;background:none;border:none;font-size:12px;color:var(--text3);cursor:pointer;padding:8px;font-family:var(--fb);transition:.2s;margin-top:4px}
.feedback-cancel:hover{color:var(--text2)}

/* ── COPY PROMPT BUTTON ──────────────────────────────── */
.prompt-block{background:var(--bg2);border:1px solid var(--border);border-radius:var(--r8);padding:12px 14px;margin:10px 0;position:relative}
.prompt-block-label{font-family:var(--fm);font-size:9px;color:var(--text3);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;display:block}
.prompt-block-text{font-size:13px;color:var(--text);line-height:1.75;white-space:pre-wrap;word-break:break-word;font-family:var(--fb)}
.prompt-copy-btn{position:absolute;top:10px;right:10px;padding:5px 12px;background:var(--accent);color:#fff;border:none;border-radius:var(--r6);font-size:11px;font-weight:500;font-family:var(--fb);cursor:pointer;transition:.2s;display:flex;align-items:center;gap:4px}
.prompt-copy-btn:hover{background:var(--accent2)}
.prompt-copy-btn.copied{background:var(--green)}
"""
    content = content.replace(
        "/* responsive */",
        new_css + "\n/* responsive */"
    )

    # ═══════════════════════════════════════════════════════════════════
    # 2. ADD HTML: milestone overlay, feedback overlay, feedback sidebar btn
    # ═══════════════════════════════════════════════════════════════════

    milestone_html = """
<!-- ════════ MILESTONE CELEBRATION ════════ -->
<div class="milestone-overlay" id="milestone-overlay">
  <div class="milestone-modal" id="milestone-modal">
    <span class="milestone-emoji" id="milestone-emoji">🔥</span>
    <div class="milestone-title" id="milestone-title">Milestone!</div>
    <div class="milestone-sub" id="milestone-sub"></div>
    <div class="milestone-body" id="milestone-body"></div>
    <div class="milestone-cta-text" id="milestone-cta"></div>
    <button class="milestone-close-btn" onclick="closeMilestone()">Continue →</button>
  </div>
</div>

<!-- ════════ FEEDBACK MODAL ════════ -->
<div class="feedback-overlay" id="feedback-overlay">
  <div class="feedback-modal">
    <h3>Tell Shubh directly.</h3>
    <p>Bug, complaint, feature idea, or just feedback — all of it reaches Shubh personally.</p>
    <div class="feedback-type-row">
      <button class="feedback-type-btn on" id="ft-bug" onclick="pickFeedbackType('bug',this)">🐛 Bug</button>
      <button class="feedback-type-btn" id="ft-feature" onclick="pickFeedbackType('feature',this)">💡 Feature</button>
      <button class="feedback-type-btn" id="ft-other" onclick="pickFeedbackType('other',this)">💬 Other</button>
    </div>
    <textarea class="feedback-ta" id="feedback-text" placeholder="Describe the issue or idea..."></textarea>
    <button class="feedback-send-btn" onclick="submitFeedback()">Send to Shubh →</button>
    <button class="feedback-cancel" onclick="closeFeedback()">Cancel</button>
  </div>
</div>
"""
    content = content.replace(
        '<!-- ════════ THREAT POPUP ════════ -->',
        milestone_html + '\n<!-- ════════ THREAT POPUP ════════ -->'
    )

    # Add feedback icon to sidebar (after upgrade icon)
    feedback_sb_icon = """      <div class="sb-icon" id="nav-feedback" onclick="openFeedback()">
        <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        <div class="sb-tip">Feedback</div>
      </div>"""

    content = content.replace(
        '      <div class="sb-icon" id="nav-upgrade" onclick="navTo(\'sc-upgrade\')">',
        feedback_sb_icon + '\n      <div class="sb-icon" id="nav-upgrade" onclick="navTo(\'sc-upgrade\')">'
    )

    # ═══════════════════════════════════════════════════════════════════
    # 3. REPLACE auth screen HTML with OTP flow
    # ═══════════════════════════════════════════════════════════════════
    old_auth_screen = '''      <!-- AUTH -->
      <div class="screen on" id="sc-auth" style="align-items:center;justify-content:center">
        <div class="auth-wrap">
                    <div class="auth-logo" style="text-align:center;margin-bottom:14px;">Zubh<em>Ai</em></div>
          <div class="auth-tagline" id="auth-tagline">7 days to transform how you work with AI.</div>

          <button class="auth-google" onclick="signInGoogle()">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Continue with Google
          </button>
          <div class="auth-divider"><span>or</span></div>
          <input class="inp" type="email" id="a-email" placeholder="Email address"/>
          <input class="inp" type="password" id="a-pass" placeholder="Password (min 6 characters)"/>
          <button class="auth-btn" id="auth-btn" onclick="handleAuth()"><span id="auth-lbl">Sign Up Free →</span></button>
          <div class="auth-err" id="auth-err"></div>
          <div class="auth-sw"><span id="auth-sw-txt">Already have an account?</span> <span class="lnk" onclick="toggleMode()" id="auth-sw-act">Login instead</span></div>
        </div>
      </div>'''

    new_auth_screen = '''      <!-- AUTH -->
      <div class="screen on" id="sc-auth" style="align-items:center;justify-content:center">
        <div class="auth-wrap">
          <div class="auth-logo" style="text-align:center;margin-bottom:6px;">Zubh<em>Ai</em></div>
          <div class="auth-tagline" style="text-align:center;margin-bottom:20px">7 days to transform how you work with AI.</div>

          <!-- Google -->
          <button class="auth-google" onclick="signInGoogle()">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Continue with Google
          </button>
          <div class="auth-divider"><span>or email</span></div>

          <!-- STEP 1: enter email -->
          <div class="otp-step show" id="otp-step-email">
            <input class="inp" type="email" id="a-email" placeholder="Your email address" autocomplete="email"/>
            <button class="auth-btn" id="otp-send-btn" onclick="sendOTP()">Send OTP →</button>
            <div class="auth-err" id="auth-err"></div>
            <div style="font-size:11px;color:var(--text3);text-align:center;margin-top:8px">We'll email you a 6-digit code. No password needed.</div>
          </div>

          <!-- STEP 2: enter OTP -->
          <div class="otp-step" id="otp-step-verify">
            <div class="otp-email-display">Code sent to <strong id="otp-sent-to"></strong></div>
            <div class="otp-digits">
              <input class="otp-digit" type="text" maxlength="1" inputmode="numeric" id="od0" oninput="otpInput(this,0)" onkeydown="otpKey(event,0)"/>
              <input class="otp-digit" type="text" maxlength="1" inputmode="numeric" id="od1" oninput="otpInput(this,1)" onkeydown="otpKey(event,1)"/>
              <input class="otp-digit" type="text" maxlength="1" inputmode="numeric" id="od2" oninput="otpInput(this,2)" onkeydown="otpKey(event,2)"/>
              <input class="otp-digit" type="text" maxlength="1" inputmode="numeric" id="od3" oninput="otpInput(this,3)" onkeydown="otpKey(event,3)"/>
              <input class="otp-digit" type="text" maxlength="1" inputmode="numeric" id="od4" oninput="otpInput(this,4)" onkeydown="otpKey(event,4)"/>
              <input class="otp-digit" type="text" maxlength="1" inputmode="numeric" id="od5" oninput="otpInput(this,5)" onkeydown="otpKey(event,5)"/>
            </div>
            <button class="auth-btn" id="otp-verify-btn" onclick="verifyOTP()" style="margin-top:4px">Verify & Start →</button>
            <div class="auth-err" id="otp-err"></div>
            <div class="otp-resend" id="otp-resend-link" onclick="resendOTP()">Resend code</div>
            <div style="font-size:11px;color:var(--text3);text-align:center;margin-top:6px;cursor:pointer" onclick="backToEmail()">← Use a different email</div>
          </div>
        </div>
      </div>'''

    if old_auth_screen in content:
        content = content.replace(old_auth_screen, new_auth_screen)
    else:
        print("WARNING: auth screen not found exactly")

    # ═══════════════════════════════════════════════════════════════════
    # 4. INJECT JavaScript — all new functions before closing </script>
    # ═══════════════════════════════════════════════════════════════════
    new_js = """
/* ═══════════════════════════════════════════════════════
   OTP AUTH
   ═══════════════════════════════════════════════════════ */
let otpEmail = '';
let otpResendTimer = null;

async function sendOTP() {
  const email = (document.getElementById('a-email')?.value || '').trim();
  const err   = document.getElementById('auth-err');
  const btn   = document.getElementById('otp-send-btn');
  err.textContent = '';
  if (!email || !/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)) {
    err.textContent = 'Enter a valid email.'; return;
  }
  btn.disabled = true; btn.textContent = 'Sending...';
  try {
    const d = await post('/auth/send-otp', { email });
    if (d.status === 'success') {
      otpEmail = email;
      document.getElementById('otp-sent-to').textContent = email;
      document.getElementById('otp-step-email').classList.remove('show');
      document.getElementById('otp-step-verify').classList.add('show');
      document.getElementById('od0').focus();
      startResendTimer();
    } else {
      err.textContent = d.message || 'Could not send OTP.';
    }
  } catch(e) {
    err.textContent = 'Network error. Try again.';
  }
  btn.disabled = false; btn.textContent = 'Send OTP →';
}

function startResendTimer() {
  const el = document.getElementById('otp-resend-link');
  el.classList.add('disabled');
  let secs = 30;
  el.textContent = `Resend in ${secs}s`;
  if (otpResendTimer) clearInterval(otpResendTimer);
  otpResendTimer = setInterval(() => {
    secs--;
    if (secs <= 0) {
      clearInterval(otpResendTimer);
      el.classList.remove('disabled');
      el.textContent = 'Resend code';
    } else {
      el.textContent = `Resend in ${secs}s`;
    }
  }, 1000);
}

async function resendOTP() {
  const btn = document.getElementById('otp-send-btn');
  document.getElementById('otp-err').textContent = '';
  const d = await post('/auth/send-otp', { email: otpEmail });
  if (d.status === 'success') { startResendTimer(); showToast('New code sent!'); }
  else { document.getElementById('otp-err').textContent = d.message; }
}

function backToEmail() {
  document.getElementById('otp-step-verify').classList.remove('show');
  document.getElementById('otp-step-email').classList.add('show');
  for (let i=0;i<6;i++) { const d=document.getElementById('od'+i); if(d) d.value=''; }
}

function otpInput(el, idx) {
  // Only allow digits
  el.value = el.value.replace(/[^0-9]/g, '');
  if (el.value && idx < 5) document.getElementById('od'+(idx+1))?.focus();
  // Auto-verify when all 6 filled
  const code = Array.from({length:6}, (_,i)=>document.getElementById('od'+i)?.value||'').join('');
  if (code.length === 6) verifyOTP();
}

function otpKey(e, idx) {
  if (e.key === 'Backspace' && !e.target.value && idx > 0) {
    document.getElementById('od'+(idx-1))?.focus();
  }
  if (e.key === 'Enter') verifyOTP();
  // Handle paste
  if (e.key.length === 1 && /[0-9]/.test(e.key) && e.target.value) {
    e.preventDefault();
    e.target.value = e.key;
    if (idx < 5) document.getElementById('od'+(idx+1))?.focus();
  }
}

async function verifyOTP() {
  const code = Array.from({length:6}, (_,i)=>document.getElementById('od'+i)?.value||'').join('');
  const err  = document.getElementById('otp-err');
  const btn  = document.getElementById('otp-verify-btn');
  err.textContent = '';
  if (code.length < 6) { err.textContent = 'Enter the full 6-digit code.'; return; }
  btn.disabled = true; btn.textContent = 'Verifying...';
  try {
    const d = await post('/auth/verify-otp', { email: otpEmail, token: code });
    if (d.status === 'success') {
      userId = d.user_id; userProfile = d.user;
      localStorage.setItem('zubhai_uid', userId);
      afterLogin();
    } else {
      err.textContent = d.message || 'Wrong code.';
      // Clear digits on wrong code
      for (let i=0;i<6;i++) { const dd=document.getElementById('od'+i); if(dd) dd.value=''; }
      document.getElementById('od0')?.focus();
    }
  } catch(e) {
    err.textContent = 'Network error. Try again.';
  }
  btn.disabled = false; btn.textContent = 'Verify & Start →';
}

// Handle OTP paste
document.addEventListener('paste', function(e) {
  const target = e.target;
  if (!target.classList.contains('otp-digit')) return;
  e.preventDefault();
  const text = (e.clipboardData || window.clipboardData).getData('text');
  const digits = text.replace(/[^0-9]/g,'').slice(0,6).split('');
  digits.forEach((d, i) => {
    const el = document.getElementById('od'+i);
    if (el) el.value = d;
  });
  if (digits.length === 6) verifyOTP();
  else if (digits.length > 0) document.getElementById('od'+digits.length)?.focus();
});

/* ═══════════════════════════════════════════════════════
   MILESTONE CELEBRATION
   ═══════════════════════════════════════════════════════ */
let milestoneShownFor = new Set();

function showMilestone(data) {
  if (!data || !data.id) return;
  // Don't show same milestone twice in session
  if (milestoneShownFor.has(data.id)) return;
  milestoneShownFor.add(data.id);

  const modal = document.getElementById('milestone-modal');
  document.getElementById('milestone-emoji').textContent = data.emoji || '🎉';
  document.getElementById('milestone-title').textContent = data.title || 'Milestone!';
  document.getElementById('milestone-sub').textContent   = data.subtitle || '';
  document.getElementById('milestone-body').textContent  = data.msg || '';
  document.getElementById('milestone-cta').textContent   = data.cta || '';
  modal.style.setProperty('--milestone-color', data.color || 'var(--accent)');

  document.getElementById('milestone-overlay').classList.add('show');
  spawnConfetti(data.color || '#e8602c');

  // Also update day badge
  const d = parseInt(data.id.replace('day',''));
  if (!isNaN(d)) document.getElementById('tb-day').textContent = d;
}

function closeMilestone() {
  document.getElementById('milestone-overlay').classList.remove('show');
}

function spawnConfetti(color) {
  const overlay = document.getElementById('milestone-overlay');
  const colors = [color, '#f97316', '#16a34a', '#3b82f6', '#d97706', '#ec4899'];
  for (let i = 0; i < 40; i++) {
    const p = document.createElement('div');
    p.className = 'confetti-piece';
    p.style.cssText = `
      left:${Math.random()*100}%;
      top:${Math.random()*30}%;
      background:${colors[Math.floor(Math.random()*colors.length)]};
      animation-duration:${2+Math.random()*2}s;
      animation-delay:${Math.random()*.8}s;
      transform:rotate(${Math.random()*360}deg);
    `;
    overlay.appendChild(p);
    setTimeout(() => p.remove(), 4000);
  }
}

/* ═══════════════════════════════════════════════════════
   COPY PROMPT BUTTON — parse [COPY_PROMPT_START]...[COPY_PROMPT_END]
   ═══════════════════════════════════════════════════════ */
function renderMessageWithCopyPrompts(text) {
  const COPY_RE = /\\[COPY_PROMPT_START\\]([\\s\\S]*?)\\[COPY_PROMPT_END\\]/g;
  let result = '', lastIndex = 0, match;

  while ((match = COPY_RE.exec(text)) !== null) {
    // text before the prompt block
    const before = text.slice(lastIndex, match.index);
    if (before) {
      result += esc(before).replace(/\\n/g,'<br/>').replace(/```([\\s\\S]*?)```/g,
        '<pre style="background:var(--bg3);border:1px solid var(--border);border-radius:6px;padding:10px;font-size:11px;overflow-x:auto;margin-top:6px;font-family:var(--fm)">$1</pre>');
    }
    // the prompt block itself
    const promptText = match[1].trim();
    const promptId   = 'pp' + Math.random().toString(36).slice(2,8);
    result += `<div class="prompt-block">
      <span class="prompt-block-label">Copy this into the AI tool ↓</span>
      <div class="prompt-block-text" id="${promptId}">${esc(promptText)}</div>
      <button class="prompt-copy-btn" onclick="copyPrompt('${promptId}',this)">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
        Copy
      </button>
    </div>`;
    lastIndex = match.index + match[0].length;
  }

  // remaining text after last prompt block
  const remaining = text.slice(lastIndex);
  if (remaining) {
    result += esc(remaining).replace(/\\n/g,'<br/>').replace(/```([\\s\\S]*?)```/g,
      '<pre style="background:var(--bg3);border:1px solid var(--border);border-radius:6px;padding:10px;font-size:11px;overflow-x:auto;margin-top:6px;font-family:var(--fm)">$1</pre>');
  }
  return result;
}

function copyPrompt(id, btn) {
  const el = document.getElementById(id);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent || '').then(() => {
    btn.classList.add('copied');
    btn.innerHTML = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
    setTimeout(() => {
      btn.classList.remove('copied');
      btn.innerHTML = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Copy`;
    }, 2200);
  }).catch(() => showToast('Copy failed — try manually'));
}

/* ═══════════════════════════════════════════════════════
   FEEDBACK MODAL
   ═══════════════════════════════════════════════════════ */
let feedbackType = 'bug';

function openFeedback() {
  closeMenu();
  document.getElementById('feedback-text').value = '';
  document.getElementById('feedback-overlay').classList.add('show');
}
function closeFeedback() {
  document.getElementById('feedback-overlay').classList.remove('show');
}
function pickFeedbackType(type, btn) {
  feedbackType = type;
  document.querySelectorAll('.feedback-type-btn').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
}
async function submitFeedback() {
  const text = (document.getElementById('feedback-text')?.value || '').trim();
  if (!text) { showToast('Write something first'); return; }
  const btn = document.querySelector('.feedback-send-btn');
  btn.disabled = true; btn.textContent = 'Sending...';
  try {
    const name  = userProfile?.name || userProfile?.email || 'Anonymous';
    const field = userProfile?.field || '';
    await post('/submit-feedback', { name, field, message: `[${feedbackType.toUpperCase()}] ${text}` });
    closeFeedback();
    showToast('Sent to Shubh. He reads everything.', 3200);
  } catch(e) {
    showToast('Error. Email hello@zubhai.com directly.');
  }
  btn.disabled = false; btn.textContent = 'Send to Shubh →';
}

/* ═══════════════════════════════════════════════════════
   PATCHED: afterLogin — Google users go to dashboard if already onboarded
   ═══════════════════════════════════════════════════════ */
"""

    # Inject the new JS right before the closing </script> of the main script block
    # Find the last </script> that doesn't have type="module"
    marker = '\n/* Three.js background loaded via ES module'
    if marker in content:
        content = content.replace(marker, new_js + marker)
    else:
        print("WARNING: Three.js marker not found, appending before last </script>")
        content = content.replace('</script>\n\n<script type="module">', new_js + '</script>\n\n<script type="module">')

    # ═══════════════════════════════════════════════════════════════════
    # 5. PATCH afterLogin to go to dashboard for already-onboarded users
    # ═══════════════════════════════════════════════════════════════════
    old_after = """function afterLogin(){
  document.getElementById('auth-btn').disabled=false;updateAuthUI();
  document.getElementById('sb').style.display='flex';
  document.getElementById('app').classList.remove('auth-mode');
  refreshSidebar();
  if(!userProfile?.onboarding_done||!userProfile?.field)startOnboarding();
  else{goHome();}
}"""

    new_after = """function afterLogin(){
  // Reset OTP UI state
  try {
    document.getElementById('otp-step-email').classList.add('show');
    document.getElementById('otp-step-verify').classList.remove('show');
    if(document.getElementById('auth-btn')) { document.getElementById('auth-btn').disabled=false; }
    updateAuthUI();
  } catch(e){}
  document.getElementById('sb').style.display='flex';
  document.getElementById('app').classList.remove('auth-mode');
  refreshSidebar();
  // If onboarded → go directly to dashboard (not launchpad)
  if(!userProfile?.onboarding_done||!userProfile?.field){
    startOnboarding();
  } else {
    goHome();
  }
}"""

    if old_after in content:
        content = content.replace(old_after, new_after)
    else:
        print("WARNING: afterLogin not found exactly")

    # ═══════════════════════════════════════════════════════════════════
    # 6. PATCH streamChatResponse to show milestone popup and use copy renderer
    # ═══════════════════════════════════════════════════════════════════

    # Patch: show milestone in stream done handler
    old_milestone_check = """            if(p.grade){
              setTimeout(lockChatAfterGrade,900);
            }
            if(p.share_post&&p.grade){"""

    new_milestone_check = """            if(p.milestone){
              setTimeout(()=>showMilestone(p.milestone),500);
            }
            if(p.grade){
              setTimeout(lockChatAfterGrade,900);
            }
            if(p.share_post&&p.grade){"""

    if old_milestone_check in content:
        content = content.replace(old_milestone_check, new_milestone_check)
    else:
        print("WARNING: milestone check patch point not found")

    # Patch: use renderMessageWithCopyPrompts in stream renderer
    old_stream_render = """                if(p.text){
                    fullText+=p.text;
                    // strip ZUBHAI_GRADE marker from display
                    const display=fullText.replace(/ZUBHAI_GRADE:[\\s\\S]*$/,'').trim();
                    innerDiv.innerHTML=esc(display)
                      .replace(/\\n/g,'<br/>')
                      .replace(/```([\\s\\S]*?)```/g,'<pre style="background:var(--bg3);border:1px solid var(--border);border-radius:6px;padding:10px;font-size:11px;overflow-x:auto;margin-top:6px;font-family:var(--fm)">$1</pre>');
                    msgs.scrollTop=msgs.scrollHeight;
                  }"""

    new_stream_render = """                if(p.text){
                    fullText+=p.text;
                    const display=fullText.replace(/ZUBHAI_GRADE:[\\s\\S]*$/,'').trim();
                    innerDiv.innerHTML=renderMessageWithCopyPrompts(display);
                    msgs.scrollTop=msgs.scrollHeight;
                  }"""

    if old_stream_render in content:
        content = content.replace(old_stream_render, new_stream_render)
    else:
        print("WARNING: stream renderer patch not found")

    # ═══════════════════════════════════════════════════════════════════
    # 7. PATCH leaderboard display to show field badges properly
    # ═══════════════════════════════════════════════════════════════════
    old_lb = """      document.getElementById('lb-list').innerHTML=d.leaderboard.map((u,i)=>`
      <div class="lb-row">
        <div class="lb-rank ${i<3?'top':''}">${medals[i]||i+1}</div>
        <div class="lb-info">
          <div class="lb-name">${esc(u.name||u.email?.split('@')[0]||'Anonymous')}</div>
          <div class="lb-sub">${esc(u.field||'—')} · Day ${u.day_in_program||1}/7 · <span class="um-plan-pill" style="font-size:8px">${(u.plan||'trial').replace('_',' ')}</span></div>
        </div>
        <div class="lb-pts">${u.points||0} pts</div>
      </div>`).join('');"""

    new_lb = """      const FIELD_EMOJI={'student':'🎓','developer':'💻','marketing':'📣','sales':'🤝'};
      document.getElementById('lb-list').innerHTML=d.leaderboard.map((u,i)=>`
      <div class="lb-row">
        <div class="lb-rank ${i<3?'top':''}">${medals[i]||'#'+(i+1)}</div>
        <div class="lb-info">
          <div class="lb-name">${esc(u.name||'Anonymous')}</div>
          <div class="lb-sub">${FIELD_EMOJI[u.field]||''} ${esc(u.field||'—')} · Day ${u.day_in_program||1}/7 · 🔥${u.streak||0}</div>
        </div>
        <div class="lb-pts" style="text-align:right">
          <div style="font-family:var(--fm);font-size:14px;color:var(--accent)">${(u.points||0).toLocaleString()}</div>
          <div style="font-size:10px;color:var(--text3);font-family:var(--fm)">${(u.plan||'trial').replace('_',' ')}</div>
        </div>
      </div>`).join('')
      + (d.total>20?`<div style="text-align:center;font-size:11px;color:var(--text3);padding:12px">Showing ${d.leaderboard.length} learners</div>`:'');"""

    if old_lb in content:
        content = content.replace(old_lb, new_lb)
    else:
        print("WARNING: leaderboard display patch not found")

    return content


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    patched = patch(html)
    out = path.replace('.html', '_patched.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(patched)
    print(f"Written: {out} ({len(patched):,} chars)")
