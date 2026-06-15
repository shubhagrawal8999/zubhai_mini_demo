from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from openai import OpenAI
import anthropic
import os, json, re, requests, resend
from datetime import date, datetime, timedelta

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
)
openai_client   = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
deepseek_client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
claude_client   = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
resend.api_key  = os.environ.get("RESEND_API_KEY")

SITE_URL     = "https://zubhai.com"
SENDER_EMAIL = "hello@zubhai.com"
SENDER_NAME  = "Shubh from Zubhai"
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "zubhai-admin-2026")

PLAN_LIMITS = {
    "free_trial": {"days": 7,  "price": 0},
    "pro":        {"days": 999, "price": 499},
    "max":        {"days": 999, "price": 999},
}

# ── MILESTONES ─────────────────────────────────────────────────────────────────
MILESTONES = {
    3: {
        "id": "day3",
        "title": "Halfway Hustler 🔥",
        "subtitle": "3 days done. Most people quit at Day 1.",
        "emoji": "🔥",
        "color": "#f97316",
        "msg": "You've completed 3 days of AI challenges. You're already ahead of 90% of people who signed up this week.",
        "cta": "Keep the streak going. Day 4 is waiting."
    },
    5: {
        "id": "day5",
        "title": "AI Power User ⚡",
        "subtitle": "5 days in. Top 10% of all Zubhai learners.",
        "emoji": "⚡",
        "color": "#e8602c",
        "msg": "5 real AI tasks completed. You've built more this week than most people do in a year of watching tutorials.",
        "cta": "2 more days. Day 7 is your portfolio piece."
    },
    7: {
        "id": "day7",
        "title": "AI Sprint Champion 🏆",
        "subtitle": "All 7 days. That's rare.",
        "emoji": "🏆",
        "color": "#16a34a",
        "msg": "You finished the full 7-day sprint. You have real, published proof of AI skills. That's what separates you now.",
        "cta": "Your Proof Wall is live. Share it on LinkedIn."
    },
}

def has_completed_day(u: dict, day: int) -> bool:
    """Check if user has already completed this specific day."""
    try:
        tc = u.get("tasks_completed", "[]")
        completed = json.loads(tc) if isinstance(tc, str) else (tc or [])
        return any(t.get("day") == day for t in completed)
    except:
        return False

def send_milestone_email(email: str, name: str, milestone: dict):
    """Send a milestone celebration email."""
    try:
        send_email(
            email,
            f"{milestone['emoji']} {milestone['title']} — Zubhai",
            email_wrap(
                f'<div class="tag">Milestone Unlocked</div>'
                f'<h1>{milestone["title"]}</h1>'
                f'<p style="font-size:16px;color:#f0f0f0">{milestone["subtitle"]}</p>'
                f'<div class="card"><p style="margin:0;font-size:14px;color:#aaa;line-height:1.8">'
                f'{milestone["msg"]}</p></div>'
                f'<p style="color:#e8602c;font-size:14px">{milestone["cta"]}</p>'
                f'<a href="{SITE_URL}" class="btn">Continue on Zubhai →</a>'
            )
        )
        return True
    except Exception as e:
        print(f"Milestone email error: {e}")
        return False

def pick_model(field: str, day: int, msg_type: str = "chat"):
    f = field.lower()
    if msg_type in ("post", "grade", "profile_parse"):
        return "gpt-4o-mini", "openai"
    if msg_type == "code" or f == "developer":
        return "claude-haiku-4-5-20251001", "claude"
    if day >= 6:
        return "claude-sonnet-4-20250514", "claude"
    return "gpt-4o-mini", "openai"

THREAT_DATA = {
    "student": {
        "risk": 52,
        "headline": "52% of entry-level jobs students target are already being automated",
        "stat": "LinkedIn 2026: AI skills add ₹3.2L avg salary premium for fresh grads",
        "fear": "Without AI skills, you're competing against candidates who do twice the work in half the time.",
        "dispatch": "IIT Bombay placement 2026: Companies explicitly asking for 'AI-native' candidates. 34% of offers went to students who demonstrated real AI workflow skills.",
        "what_ai_does": "AI writes essays, solves coding problems, analyzes case studies, researches at PhD level. Students who use it produce work that looks senior.",
    },
    "developer": {
        "risk": 71,
        "headline": "71% of junior dev tasks can be fully automated by AI coding tools today",
        "stat": "GitHub Copilot users ship 55% more code per day. Teams using it cut junior headcount.",
        "fear": "Companies hire 1 senior dev with AI instead of 3 junior devs.",
        "dispatch": "Wipro, Infosys Q1 2026: Both reduced fresher intake by 28%. Reason: AI tools handling what freshers used to do.",
        "what_ai_does": "AI writes boilerplate, debugs, documents, tests, reviews code. Devs who orchestrate AI survive. Those who compete with it don't.",
    },
    "marketing": {
        "risk": 68,
        "headline": "68% of marketing tasks — content, copy, analysis — are now AI-automatable",
        "stat": "HubSpot 2026: Marketing teams using AI produce 7x more content with same headcount",
        "fear": "Your competitor's 2-person team is outproducing your 8-person team.",
        "dispatch": "Meta Ads 2026: AI-generated ad copy outperforming human copy in 61% of A/B tests.",
        "what_ai_does": "AI writes ads, creates social content, analyzes campaigns, builds email sequences. Marketers who use it work like a 10-person team.",
    },
    "sales": {
        "risk": 45,
        "headline": "45% of sales tasks — prospecting, follow-ups, CRM updates — are now AI-handled",
        "stat": "Salesforce 2026: Reps using AI close 23% more deals, spend 40% less time on admin",
        "fear": "Your quota went up 30% but your time didn't. The reps hitting target are using AI.",
        "dispatch": "Apollo.io 2026: AI-personalized outreach getting 3.4x reply rate vs generic cold email.",
        "what_ai_does": "AI researches prospects, writes personalized outreach, handles objections, updates CRM, predicts close probability.",
    },
}

PROGRAM = {
    "student": [
        {"day":1,"title":"Your AI Research Partner","tool":"Perplexity","why":"The fastest students in 2026 don't read textbooks — they query AI and get cited, current answers in 10 minutes. This is the skill that cuts your research time by 70%.","task":"Use Perplexity to research a topic from your current course. Don't just Google — use Perplexity's follow-up questions to go 3 layers deep. Get specific, cited sources.","starter":"Go to perplexity.ai → search your hardest topic right now → ask 3 follow-up questions → paste the best answer thread here.","verify":"Paste your Perplexity result or share the thread link","personalize_by":["current_course","learning_goal"]},
        {"day":2,"title":"Write Better Than 90% of Your Batch","tool":"Claude","why":"Recruiters spend 6 seconds on a resume. Professors spend 30 seconds on an intro. AI can make your writing look like it came from someone 5 years ahead of you.","task":"Take something you wrote recently — an assignment, an email, a summary. Paste it into Claude. Ask it to rewrite it to be 10x clearer and more compelling. Compare the two.","starter":"Paste any text you wrote into Claude with: 'Rewrite this to be clearer, more specific, and more professional. Show me what I missed.'","verify":"Share your original text + Claude's rewrite (or just the rewrite with one line about what changed)","personalize_by":["writing_weakness","current_course"]},
        {"day":3,"title":"Learn Any Hard Concept in 20 Minutes","tool":"ChatGPT","why":"The students who master exams fastest aren't the ones who study longest — they're the ones who get concepts explained 3 different ways until something clicks.","task":"Pick the hardest concept in your current course. Ask ChatGPT to explain it in 3 ways: like you're 10, like you're a student, and with a real-world example. Don't stop until you can explain it back in your own words.","starter":"Go to ChatGPT → 'Explain [your concept] to me 3 ways: simple analogy, technical explanation, real example. Then ask me a question to check if I got it.'","verify":"Write your 5-sentence plain-English explanation of the concept — no AI, just you","personalize_by":["hardest_subject","exam_upcoming"]},
        {"day":4,"title":"Build Your AI-Powered LinkedIn Presence","tool":"Claude","why":"Students who post on LinkedIn during college get 2-3x more interview calls. Most don't because they think they have nothing to say. AI fixes that.","task":"Use Claude to write 3 LinkedIn posts about something you learned this week. Even Day 1–3 of this program counts. AI can make your insights sound like a thought leader.","starter":"Tell Claude: 'I'm a [your field] student. I just learned [what you learned this week]. Write 3 LinkedIn post drafts — short, specific, human, no corporate speak.'","verify":"Share your 3 drafted posts (or post one and share the URL)","personalize_by":["career_goal","industry_interest"]},
        {"day":5,"title":"Automate Your Study Schedule","tool":"ChatGPT","why":"Most students waste 40% of study time on the wrong topics. AI can build a personalized schedule from your syllabus in 5 minutes that a study consultant would charge ₹5000 for.","task":"Paste your syllabus (or just list your subjects and exam dates) into ChatGPT. Ask for a complete day-by-day study plan with revision cycles and weak-area focus.","starter":"ChatGPT prompt: 'Here's my syllabus: [paste it]. My exams start [date]. Build me a study plan with daily targets, spaced repetition, and revision windows. Flag my high-risk topics.'","verify":"Share your study plan (screenshot or text)","personalize_by":["exam_dates","weak_subjects"]},
        {"day":6,"title":"AI Mock Interview","tool":"Claude","why":"Most students fail interviews not because they lack knowledge but because they've never practiced. Claude will grill you harder than any real interviewer and give you specific feedback.","task":"Have Claude conduct a full mock interview for your target job or internship. You answer in the chat like it's real. It gives you specific feedback after each answer.","starter":"Tell Claude: 'Conduct a 5-question mock interview for a [role] internship at [company type]. Ask one question at a time. After each answer give specific feedback. Be honest, not kind.'","verify":"Share the interview transcript or your overall feedback","personalize_by":["target_role","target_company_type"]},
        {"day":7,"title":"Publish Your AI-Powered Research Piece","tool":"Perplexity + Claude","why":"This is your proof. A published piece with your name on it, showing you can research and write at a professional level. This goes on your resume, your LinkedIn, your proof wall.","task":"MILESTONE: Pick a real problem in your industry. Use Perplexity to research it deeply (3 layers, cited sources). Use Claude to turn your research into a structured article. Publish on LinkedIn or Medium.","starter":"Perplexity → deep research → export key points → Claude → 'Turn these research notes into a 400-word LinkedIn article about [topic]. Professional tone, specific data, clear insight.'","verify":"Share the published URL — this goes on your Proof Wall permanently","personalize_by":["career_goal","industry_interest","current_course"]},
    ],
    "developer": [
        {"day":1,"title":"Read Any Codebase Instantly","tool":"Claude","why":"Senior devs spend less time writing code and more time reading it. AI lets you understand any codebase in 10 minutes — a skill that makes you look like you've been on the project for months.","task":"Pick any public GitHub repo (your own project, a library you use, or anything interesting). Paste one file into Claude and ask it to explain what it does, why it's structured this way, and what you'd change.","starter":"Go to any GitHub repo → pick a .py/.js/.ts file → paste into Claude → 'Explain this file: what it does, why it's designed this way, what bugs or improvements you see. Be specific.'","verify":"Share Claude's explanation + your 2-line reaction (did it match your understanding?)","personalize_by":["primary_language","experience_level"]},
        {"day":2,"title":"Debug Without Stack Overflow","tool":"Claude","why":"Junior devs spend 40% of their time on bugs that Claude can root-cause in 30 seconds. The skill is knowing HOW to give Claude the right context.","task":"Find any error you've seen recently (real or from a past project). Paste the error + the relevant code into Claude. Ask for root cause analysis, not just a fix.","starter":"Paste into Claude: '[Error message]\n\n[Your code]\n\nDon't just fix this — explain WHY it's happening, what I misunderstood, and what I should check for next time.'","verify":"Share the error + Claude's root cause analysis + whether the fix worked","personalize_by":["primary_language","current_project"]},
        {"day":3,"title":"Generate Tests You Actually Understand","tool":"ChatGPT","why":"Most devs skip tests because writing them is slow. AI writes tests in 2 minutes. Once you see the test output, you start thinking in tests — which makes your code better.","task":"Take any function you've written (20+ lines). Paste it into ChatGPT Code Interpreter. Ask it to generate unit tests with edge cases, and explain what each test is checking.","starter":"Paste into ChatGPT: '[Your function]\n\nGenerate unit tests for this. Cover: happy path, edge cases, error cases. Use [pytest/jest/your framework]. Explain what each test checks and why.'","verify":"Share the test file + one thing the AI caught that you hadn't thought of","personalize_by":["primary_language","testing_framework"]},
        {"day":4,"title":"Document Code Nobody Hates Reading","tool":"Claude","why":"Undocumented code is a career liability. Senior devs judge you by your docs. AI can turn your worst spaghetti into clean, professional documentation in 5 minutes.","task":"Take your worst-documented code (a messy function, an undocumented module, anything). Use Claude to generate a README, inline docstrings, and explain the design decisions.","starter":"Paste into Claude: '[Your messy code]\n\nGenerate: (1) a README section for this, (2) inline docstrings, (3) a one-paragraph explanation of the design decisions. Be honest about weaknesses.'","verify":"Share the before/after docs","personalize_by":["primary_language","current_project"]},
        {"day":5,"title":"AI Code Review Like a Senior","tool":"Claude","why":"A senior dev code review catches bugs, security holes, and bad patterns you've been blind to. Claude gives you that review in 60 seconds — brutally honest, no feelings.","task":"Submit your most recent code (PR, file, feature — anything 50+ lines) to Claude for a full senior-level review. Security, performance, readability, real-world edge cases.","starter":"Paste into Claude: '[Your code]\n\nCode review this like a staff engineer at a top company. Check: security vulnerabilities, performance issues, naming, edge cases, maintainability. Give line-specific feedback. Be harsh.'","verify":"Share the review output + one improvement you actually made based on it","personalize_by":["primary_language","experience_level","current_project"]},
        {"day":6,"title":"Ship an AI-Powered Feature","tool":"Claude","why":"AI features are the new CRUD. Every product is adding them. The devs who can ship AI features (summarizer, chatbot, classifier) are commanding ₹2-5L salary premium right now.","task":"Add one AI-powered feature to any project: a summarizer, a simple chatbot, a text classifier, an autocomplete, a code explainer. Use Claude to write the integration code.","starter":"Tell Claude: 'I'm building [your project in your language]. Help me add a [feature] using the Anthropic/OpenAI API. Give me the complete working code with error handling. Explain each part.'","verify":"Share working code or a demo URL — even a simple script counts","personalize_by":["primary_language","current_project","experience_level"]},
        {"day":7,"title":"Your AI Dev Showcase","tool":"Claude + GitHub","why":"MILESTONE: This is your proof. A documented AI-assisted project on GitHub with a real README is worth more than any certification when talking to a technical recruiter.","task":"Document your best work from this week. Clean up one project with AI help — proper README, docstrings, and a working demo. Write a LinkedIn post about what you built and what you learned.","starter":"Claude: 'Write a professional GitHub README for this project: [describe it]. Include: what it does, how to run it, tech stack, what I learned, screenshots section.' Then push to GitHub.","verify":"Share GitHub URL + LinkedIn post URL — both go on your Proof Wall","personalize_by":["primary_language","current_project","career_goal"]},
    ],
    "marketing": [
        {"day":1,"title":"Write a Month of Content in One Sitting","tool":"Claude","why":"The marketers winning in 2026 aren't posting more — they're posting smarter. AI lets you batch a month of content in 2 hours instead of scrambling daily.","task":"Use Claude to generate 30 content ideas for your brand (or any brand you work with). Then write 5 full posts — LinkedIn, Instagram, or Twitter. Pick the platform that matters for your goal.","starter":"Tell Claude: 'I'm creating content for [brand/industry]. Target audience: [who]. Goal: [awareness/leads/sales]. Generate 30 post ideas across topics: educational, opinion, behind-scenes, social proof, trending. Then write the top 5 as full posts.'","verify":"Share 3 drafted posts or post one and share the URL","personalize_by":["industry","target_audience","content_goal"]},
        {"day":2,"title":"Ad Copy That Actually Converts","tool":"Claude","why":"Most ad copy is generic. The copy that converts uses specific psychological angles — fear, aspiration, curiosity, social proof. AI can write all 5 angles in 5 minutes so you can test what works.","task":"Pick a real product (yours, a client's, or any brand). Write 5 ad copy variants using different angles. Grade them yourself on: specificity, hook strength, CTA clarity.","starter":"Tell Claude: 'Write 5 ad copy variants for [product]. One for each angle: (1) fear/loss, (2) aspiration, (3) social proof, (4) curiosity/intrigue, (5) direct/logical. Each: headline + 2 lines + CTA. Make them feel human, not AI.'","verify":"Share your 5 variants + your pick for strongest and why","personalize_by":["industry","product_type","target_audience"]},
        {"day":3,"title":"Know Your Competitor Better Than They Know Themselves","tool":"Perplexity","why":"The best marketing insight comes from gaps — what your competitor isn't saying. Perplexity can surface their positioning, messaging, weaknesses, and audience complaints in 30 minutes.","task":"Pick your top 1-3 competitors. Use Perplexity to build a complete competitive analysis: their positioning, messaging angles, customer complaints, what they're NOT saying, and the gap you can own.","starter":"Perplexity: 'Analyze [Competitor X] marketing: (1) their core positioning statement, (2) what customer reviews say they fail at, (3) their top content topics, (4) what audience segments they ignore. Give sources.'","verify":"Share your analysis or Perplexity thread — even bullet points count","personalize_by":["industry","competitor_names","target_audience"]},
        {"day":4,"title":"Email Sequence That Sells","tool":"Claude","why":"Email is still the highest ROI channel (₹3600 return per ₹100 spent). Most email sequences fail because they're generic. AI can write a personalized 5-email sequence in 15 minutes.","task":"Build a 5-email welcome/nurture sequence for a real product. Each email should have a clear purpose: welcome, educate, overcome objection, social proof, close.","starter":"Tell Claude: 'Write a 5-email welcome sequence for [product]. Email 1: welcome + quick win. Email 2: educate on main benefit. Email 3: overcome top objection ([objection]). Email 4: social proof + case study. Email 5: offer + urgency. Each email: subject line + 150-word body + CTA.'","verify":"Share your sequence (doc link or paste 2 of the 5 emails)","personalize_by":["industry","product_type","customer_objections"]},
        {"day":5,"title":"Turn Data Into Strategy in 10 Minutes","tool":"ChatGPT","why":"Most marketers collect data but never extract insight. ChatGPT Code Interpreter can turn raw campaign numbers into a clear 'what's working, what to cut, what to double down on' in minutes.","task":"Feed ChatGPT your campaign data (Meta/Google Ads, email stats, social analytics — real or realistic numbers). Ask for plain-English analysis and prioritized next steps.","starter":"Paste into ChatGPT: '[Your data table or numbers]. Analyze this. Tell me: (1) top 3 things working, (2) top 3 things to cut, (3) one thing to double down on, (4) what I'm not measuring that I should be. Plain English, no jargon.'","verify":"Share the analysis output + one decision you'd make based on it","personalize_by":["current_channels","key_metrics"]},
        {"day":6,"title":"Build a Full Campaign in One Hour","tool":"Claude","why":"Agencies charge ₹50,000+ for a campaign brief. You're going to build one end-to-end in 60 minutes using AI — strategy, copy, visual direction, targeting. This is the portfolio piece.","task":"Pick a real brand (yours, a client's, or a brand you love). Build a complete campaign: goal, target audience, messaging, 3 ad creatives, email subject lines, social copy, targeting brief.","starter":"Tell Claude: 'I'm building a campaign for [brand]. Goal: [awareness/leads/sales]. Budget: [realistic number]. Target: [audience]. Build: (1) core messaging framework, (2) 3 ad creative briefs, (3) 5 email subject line options, (4) 3 social posts, (5) targeting recommendation.' Then iterate.","verify":"Share your campaign document or brief","personalize_by":["industry","target_audience","campaign_goal"]},
        {"day":7,"title":"Publish Your AI Marketing Case Study","tool":"Claude + Perplexity","why":"MILESTONE: A real case study with your name on it is worth 10 certifications. Marketers who publish case studies get hired faster, command higher rates, and build audiences.","task":"Research a real brand's marketing challenge using Perplexity. Build a complete AI-powered strategy for solving it. Write it up as a case study and publish on LinkedIn.","starter":"Perplexity: research [brand's] current marketing challenge → Claude: 'Turn these research notes into a 500-word marketing case study: problem, AI-powered solution, expected results, key insight.' → publish.","verify":"Share the LinkedIn post URL — this is your Proof Wall","personalize_by":["industry","career_goal"]},
    ],
    "sales": [
        {"day":1,"title":"Find 50 Qualified Leads in One Hour","tool":"Perplexity","why":"Cold prospecting is the #1 time sink for SDRs. Perplexity can surface qualified leads with buying signals — funding, hiring, expansion news — in minutes, not days.","task":"Define your ideal customer profile. Use Perplexity to find 20-50 companies that match it, specifically looking for buying signals: recent funding, new hires in your buyer's role, product launches.","starter":"Perplexity: 'Find [industry] companies in India that [raised Series A in 2025-2026 / recently hired a Head of X / expanded to new market]. Give: company name, size, signal, why they'd need [your product/service].'","verify":"Share your prospect list (anonymized ok) or the Perplexity research thread","personalize_by":["industry","icp","product_type"]},
        {"day":2,"title":"Cold Outreach That Gets Replies","tool":"Claude","why":"Generic cold emails get 2% reply rates. Personalized, signal-based outreach gets 20%+. AI can write 10 hyper-personalized messages in 10 minutes using the research you did yesterday.","task":"Take 5 prospects from Day 1. Write a personalized cold email or LinkedIn DM for each — different hook for each one based on their specific signal or pain point.","starter":"Tell Claude: 'Write a cold email for [prospect company]. Their buying signal: [what you found]. My product: [what you sell]. Constraints: subject line under 6 words, first line about THEM not me, body 3 sentences max, CTA = 1 question not a meeting ask. No corporate speak.'","verify":"Share 3 examples of your outreach messages","personalize_by":["product_type","icp","tone_preference"]},
        {"day":3,"title":"Research Any Prospect in 5 Minutes","tool":"Perplexity","why":"The best sales call starts before the call. Knowing their recent news, their pain, their competition, and their decision-maker's priorities makes you sound like an insider, not a vendor.","task":"Pick 3 real upcoming prospects or calls. Build a complete research card for each: company news, recent hires, competitive pressure, potential pain, decision-maker background.","starter":"Perplexity: 'Research [Company X] for a sales call. Give me: (1) recent news/announcements, (2) likely pain points based on their industry/size, (3) who I should actually be talking to, (4) one thing their competitors are doing that they might feel pressure about.'","verify":"Share one complete prospect research card","personalize_by":["industry","deal_size","sales_cycle"]},
        {"day":4,"title":"Build Your Sales Battle Card","tool":"Claude","why":"The best salespeople don't improvise objection handling — they have a prepared response for every scenario. AI can build your complete battle card in 20 minutes.","task":"List your top 10 objections you actually hear. Use Claude to build a complete response playbook — not generic rebuttals but specific, contextual responses that move the conversation forward.","starter":"Tell Claude: 'I sell [product] to [ICP]. My top objections: [list them]. For each, write: (1) why they're really saying this (real concern behind objection), (2) best response (empathize → reframe → evidence), (3) follow-up question to keep them talking. Be specific, not generic.'","verify":"Share your battle card (doc link or paste 3 entries)","personalize_by":["product_type","icp","common_objections"]},
        {"day":5,"title":"Follow-Up Sequences That Close","tool":"Claude","why":"80% of deals close on the 5th-12th follow-up. Most reps stop at 2. AI can write a complete 7-touch sequence that doesn't feel like nagging — each touch adds new value.","task":"Build a 7-touch follow-up sequence for a real prospect who went quiet after showing interest. Day 1, 3, 7, 14, 21, 30, 60 — different angle and value each time.","starter":"Tell Claude: 'Write a 7-touch follow-up sequence for a prospect who showed interest but went quiet. They're a [title] at [company type]. Each touchpoint: day number, subject/opening line, core message (new angle or value each time), CTA. No just following up allowed.'","verify":"Share your complete sequence","personalize_by":["icp","deal_size","product_type"]},
        {"day":6,"title":"Prep for Any Sales Call in 10 Minutes","tool":"Perplexity + Claude","why":"Top closers spend as much time on pre-call prep as on the call itself. AI lets you do full research + call planning in 10 minutes — questions, objection prep, opening, close strategy.","task":"Pick a real upcoming call or a prospect you want to land. Use Perplexity to research them fully. Use Claude to build your call plan: agenda, questions, potential objections, ideal close.","starter":"Perplexity research → paste into Claude: 'I have a call with [role] at [company]. Here's my research: [paste]. Build: (1) 3 opening questions that show I've done my homework, (2) the key pain I'm targeting, (3) objections I'll probably face + my responses, (4) how I close this call — specific ask.'","verify":"Share your call prep document","personalize_by":["icp","deal_size","sales_cycle"]},
        {"day":7,"title":"Your AI Sales Playbook","tool":"Claude","why":"MILESTONE: A documented AI-powered sales process is your differentiator. Share it publicly and you become the person who gets AI + sales — which is extremely rare.","task":"Compile everything you built this week into a complete sales playbook. Add a LinkedIn post about how AI changed your outreach, research, and close rates.","starter":"Tell Claude: 'I want to write a LinkedIn post about using AI in my sales process. Here's what I did this week: [summarize Days 1-6]. Write a post that is specific, honest, shows real results or learnings. 4-5 lines max. No humblebrag.' Then share the full playbook.","verify":"Share your LinkedIn post URL — this is your Proof Wall","personalize_by":["industry","career_goal"]},
    ],
}

DEFAULT_PROFILE = {
    "track": "", "skill_level": "beginner", "current_role": "", "goal": "",
    "tools_known": [], "tools_to_learn": [], "current_project": "",
    "pain_point": "", "industry": "", "timeline": "flexible",
    "language": "English", "raw_answer": "",
}


# ── JOURNEY HELPERS ────────────────────────────────────────────────────────────

def get_journey_history(user_id: str, limit: int = 10) -> list:
    """Full history of what user built, where they struggled, scores."""
    try:
        r = supabase.table("user_journey").select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return r.data or []
    except Exception as e:
        print(f"Journey fetch error: {e}")
        return []


def store_journey(user_id: str, day: int, field: str, task_title: str,
                  prompt_generated: str, user_output: str, score: int,
                  where_stuck: str = "", breakthrough: str = "",
                  time_spent: int = 0, iterations: int = 1):
    try:
        insight = extract_session_insight(user_output, score, field, day)
        supabase.table("user_journey").insert({
            "user_id": user_id,
            "day": day,
            "field": field,
            "task_title": task_title,
            "prompt_generated": prompt_generated,
            "user_output": user_output[:5000],
            "score": score,
            "time_spent_minutes": time_spent,
            "iterations": iterations,
            "where_stuck": where_stuck,
            "breakthrough": breakthrough,
            "ai_insight": insight,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # update collective patterns
        update_collective_patterns(field, day, where_stuck, score)
    except Exception as e:
        print(f"Journey store error: {e}")


def extract_session_insight(output: str, score: int, field: str, day: int) -> str:
    """What did we learn about this person from their submission?"""
    if not output or len(output) < 50:
        return ""
    try:
        r = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"""
Analyze this Day {day} {field} submission (score {score}/10).
In 2 sentences only:
- What is this person strong at?
- What specific thing do they avoid or struggle with?

Submission: {output[:1000]}

Return ONLY 2 sentences. No headers, no preamble."""}],
            max_tokens=100, temperature=0.2
        )
        return r.choices[0].message.content.strip()
    except:
        return ""


def update_collective_patterns(field: str, day: int, where_stuck: str, score: int):
    """Aggregates struggle patterns across all users."""
    if not where_stuck:
        return
    try:
        existing = supabase.table("collective_patterns").select("*") \
            .eq("field", field).eq("day", day) \
            .eq("pattern_type", "struggle").execute()

        if existing.data:
            row = existing.data[0]
            new_text = row["pattern_text"] + " | " + where_stuck
            supabase.table("collective_patterns").update({
                "pattern_text": new_text[:2000],
                "sample_size": row["sample_size"] + 1,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", row["id"]).execute()
        else:
            supabase.table("collective_patterns").insert({
                "field": field, "day": day,
                "pattern_type": "struggle",
                "pattern_text": where_stuck,
                "sample_size": 1
            }).execute()
    except Exception as e:
        print(f"Pattern update error: {e}")


def get_collective_patterns(field: str, day: int) -> str:
    """What do similar users struggle with on this day?"""
    try:
        r = supabase.table("collective_patterns").select("*") \
            .eq("field", field).eq("day", day).execute()
        if not r.data:
            return ""
        patterns = [row["pattern_text"] for row in r.data if row.get("sample_size", 0) >= 3]
        return "; ".join(patterns[:2]) if patterns else ""
    except:
        return ""


# ── AGENT BRAIN — DYNAMIC PROMPT GENERATOR ───────────────────────────────────

def generate_task_prompt(profile: dict, day_info: dict, field: str,
                          day: int, journey_history: list) -> str:
    """
    Generates a personalized, interactive prompt for the user to copy
    into their external AI tool. NOT pre-written — built fresh from their data.
    """
    name        = profile.get("name", "")
    company     = profile.get("company", "")
    role        = profile.get("current_role", field + " professional")
    goal        = profile.get("goal", "")
    product     = profile.get("product_name", "")
    audience    = profile.get("target_audience", "")
    industry    = profile.get("industry", field)
    level       = profile.get("skill_level", "beginner")
    time_budget = profile.get("daily_time_budget", "20 minutes")
    language    = profile.get("language", "English")
    tool        = day_info.get("tool", "Claude")

    # Build what we know about their journey
    journey_ctx = ""
    if journey_history:
        recent = journey_history[:3]
        lines = []
        for j in recent:
            stuck = j.get("where_stuck", "")
            insight = j.get("ai_insight", "")
            lines.append(
                f"Day {j['day']}: scored {j.get('score', 0)}/10"
                + (f", struggled with: {stuck}" if stuck else "")
                + (f", insight: {insight}" if insight else "")
            )
        journey_ctx = "\n".join(lines)

    # What similar users struggled with
    collective = get_collective_patterns(field, day)

    generation_prompt = f"""You are building a personalized AI task prompt for one specific person.

PERSON:
Name: {name or 'not provided'}
Role: {role}
Company / Product: {company or product or 'their work'}
Industry: {industry}
Goal: {goal or f'get better at {field} using AI tools'}
Target Audience: {audience or 'their customers'}
Skill Level: {level}
Time today: {time_budget}
Language preference: {language}

THEIR JOURNEY SO FAR:
{journey_ctx if journey_ctx else "First session — no history yet."}

COMMON STRUGGLES (from similar users at this day):
{collective if collective else "None recorded yet."}

TODAY'S TASK:
Day {day} of their 7-day intro sprint — {day_info['title']}
Why it matters: {day_info['why']}
What they need to do: {day_info['task']}
Tool: {tool}

WRITE A PROMPT they will copy-paste into {tool}.

RULES FOR THE PROMPT YOU WRITE:
1. Open with exactly who they are — use their REAL name, company, product.
   No placeholders. No [your product here]. Use the actual values above.

2. Tell {tool} to search the web FIRST for 2026 data relevant to their
   specific industry and goal. Name what to look for.

3. Have {tool} ask them 2-3 questions ONE AT A TIME.
   - Do not ask things we already know (we know their product, role, goal).
   - Ask only what's missing for THIS specific task.
   - Each question: "Wait for my answer before continuing."

4. After all answers, produce something REAL:
   - Their actual deliverable (their email sequence, their ad copy, their code)
   - Using their real product name and real audience throughout
   - Not a generic example — this should only work for them

5. End with a shareable artifact (LinkedIn post, shareable doc, template
   they can actually use tomorrow in their real work)

6. Tone: senior professional giving a real task. Zero fluff.
   Do not say "master this in 7 days" — this is a sprint intro, not mastery.

7. If language preference is not English, end the prompt with:
   "Respond entirely in {language}."

Output ONLY the prompt text. Nothing else. No explanation."""

    try:
        r = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=900,
            messages=[{"role": "user", "content": generation_prompt}]
        )
        return r.content[0].text.strip()
    except Exception as e:
        print(f"Prompt generation error: {e}")
        # Fallback — basic starter from PROGRAM
        return day_info.get("starter", "Complete today's task and paste your result here.")


def extract_json(text):
    if not text:
        return None
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except:
        pass
    try:
        s, e = text.find("{"), text.rfind("}") + 1
        if s != -1 and e > s:
            return json.loads(text[s:e])
    except:
        pass
    return None

def today_str():
    return date.today().isoformat()

def get_user(user_id: str):
    r = supabase.table("users").select("*").eq("id", user_id).execute()
    return r.data[0] if r.data else None

def get_profile(u: dict) -> dict:
    raw = u.get("profile")
    if not raw:
        return dict(DEFAULT_PROFILE)
    try:
        p = json.loads(raw) if isinstance(raw, str) else raw
        return {**DEFAULT_PROFILE, **p}
    except:
        return dict(DEFAULT_PROFILE)

def send_email(to: str, subject: str, html: str):
    try:
        resend.Emails.send({"from": f"{SENDER_NAME} <{SENDER_EMAIL}>", "to": [to], "subject": subject, "html": html})
        return True
        
    except Exception as e:
        print(f"Email error: {e}")
        return False

def email_wrap(content: str) -> str:
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<style>
body{{margin:0;padding:0;background:#0a0a0a;font-family:-apple-system,sans-serif}}
.w{{max-width:560px;margin:0 auto;background:#111;border:1px solid #222;border-radius:12px;overflow:hidden}}
.h{{padding:20px 28px;background:#111;border-bottom:1px solid #1e1e1e}}
.logo{{font-size:18px;font-weight:600;color:#fff;letter-spacing:-.3px}}
.logo em{{color:#e8602c;font-style:normal}}
.b{{padding:28px}}
.f{{padding:20px 28px;background:#0a0a0a;border-top:1px solid #1e1e1e;text-align:center}}
.f p{{color:#555;font-size:11px;margin:4px 0}}
.f a{{color:#888;text-decoration:none}}
h1{{color:#f0f0f0;font-size:22px;font-weight:500;margin:0 0 12px;letter-spacing:-.3px}}
p{{color:#888;font-size:14px;line-height:1.8;margin:0 0 12px}}
.btn{{display:inline-block;background:#e8602c;color:#fff;font-weight:500;font-size:14px;padding:12px 28px;border-radius:8px;text-decoration:none;margin:14px 0}}
.card{{background:#161616;border:1px solid #222;border-radius:8px;padding:18px;margin:14px 0}}
.tag{{display:inline-block;background:rgba(232,96,44,.1);border:1px solid rgba(232,96,44,.2);color:#e8602c;font-size:10px;padding:3px 10px;border-radius:100px;margin-bottom:14px;letter-spacing:1px;text-transform:uppercase}}
</style></head><body>
<div style="padding:24px">
<div class="w">
<div class="h"><span class="logo">Zub<em>hai</em></span></div>
<div class="b">{content}</div>
<div class="f"><p>Built in India 🇮🇳 by <a href="https://linkedin.com/in/shubhagrawal429">Shubh Agrawal</a></p>
<p><a href="mailto:hello@zubhai.com">Reply anytime</a> · <a href="{SITE_URL}">{SITE_URL}</a></p></div>
</div></div></body></html>"""

def build_personalization_context(profile: dict, day_info: dict, field: str, day: int) -> str:
    parts = []
    role = profile.get("current_role", "")
    if role:
        parts.append(f"Their role: {role}")
    level = profile.get("skill_level", "beginner")
    parts.append(f"Skill level: {level}")
    goal = profile.get("goal", "")
    if goal:
        parts.append(f"Goal: {goal}")
    pain = profile.get("pain_point", "")
    if pain:
        parts.append(f"Pain point: {pain}")
    tools_k = profile.get("tools_known", [])
    if tools_k:
        parts.append(f"Tools they already know: {', '.join(tools_k)}")
    tools_w = profile.get("tools_to_learn", [])
    if tools_w:
        parts.append(f"Tools they want to learn: {', '.join(tools_w)}")
    proj = profile.get("current_project", "")
    if proj:
        parts.append(f"Current project: {proj}")
    industry = profile.get("industry", "")
    if industry:
        parts.append(f"Industry: {industry}")
    if level == "beginner":
        parts.append("→ Give step-by-step. Don't assume they know tools. When giving starter, be explicit about WHERE to go and WHAT to type.")
    elif level == "intermediate":
        tools_ref = f"They know {', '.join(tools_k[:2])} — connect today's task to their existing stack." if tools_k else ""
        parts.append(f"→ Skip basic explanations. Go straight to the interesting part. {tools_ref}")
    elif level == "advanced":
        parts.append("→ Give them the advanced version. Challenge them. If they know it, push them to go deeper or faster.")
    if proj:
        personalize_by = day_info.get("personalize_by", [])
        if "current_project" in personalize_by:
            parts.append(f"→ IMPORTANT: Use their project '{proj}' as the example for today's task. Don't give them a hypothetical — use their real work.")
    return "\n".join(parts)


def fetch_daily_news(field: str, profile: dict) -> dict:
    """
    Return daily news context for a user's field.
    Currently uses static THREAT_DATA; can be extended to pull from an external API.
    """
    f = field.lower()
    threat = THREAT_DATA.get(f, THREAT_DATA["student"])
    
    # Build a highlights list from relevant threat data
    highlights = [
        threat.get("what_ai_does", ""),
        threat.get("stat", ""),
        threat.get("dispatch", "")
    ]
    highlights = [h for h in highlights if h]  # remove empty strings
    
    return {
        "headline": threat.get("headline", "AI is reshaping your industry"),
        "highlights": highlights,
        "risk": threat.get("risk", 0),
        "fear": threat.get("fear", ""),
    }

# ── STATIC ─────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return FileResponse("/app/index.html")

# ── IMAGE UPLOAD SUPPORT ───────────────────────────────────────────────────────
@app.post("/chat/image")
async def chat_image(data: dict):
    user_id    = data.get("user_id")
    message    = data.get("message", "Please review this screenshot and give feedback.").strip()
    image_b64  = data.get("image_base64", "")
    image_type = data.get("image_type", "image/png")
    day        = int(data.get("day", 1))
    field      = data.get("field", "student")
    language   = data.get("language", "English")
    history    = data.get("history", [])

    if not user_id or not image_b64:
        return JSONResponse({"status": "error", "message": "Missing image or user_id"})

    u = get_user(user_id)
    if not u:
        return JSONResponse({"status": "error", "message": "User not found"})

    profile  = get_profile(u)
    f        = field.lower()
    program  = PROGRAM.get(f, PROGRAM["student"])
    day_idx  = min(max(day - 1, 0), len(program) - 1)
    day_info = program[day_idx]
    pers     = build_personalization_context(profile, day_info, f, day)

    system = f"""You are Arjun — mentor at Zubhai. You can see images and screenshots the user shares.
TODAY — Day {day}/7: {day_info['title']}
Task: {day_info['task']}
USER PROFILE:
{pers}
When reviewing a screenshot:
- Be specific about what you SEE in it
- Give actionable, direct feedback
- Reference exact elements visible (headlines, text, layout, etc.)
- Keep it punchy — no corporate feedback
Language: {u.get('language', language)}"""

    messages = []
    for m in history[-6:]:
        messages.append({"role": m["role"], "content": m["content"]})

    messages.append({
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_type,
                    "data": image_b64,
                }
            },
            {"type": "text", "text": message}
        ]
    })

    async def generate():
        try:
            with claude_client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                system=system,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'text': text})}\n\n"

            supabase.table("users").update({"last_active": today_str()}).eq("id", user_id).execute()
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            print(f"Image chat error: {e}")
            yield f"data: {json.dumps({'error': 'Could not process image. Try again.'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache", "Connection": "keep-alive",
            "X-Accel-Buffering": "no", "Access-Control-Allow-Origin": "*",
        }
    )

# ── GOOGLE AUTH ────────────────────────────────────────────────────────────────
@app.post("/auth/google")
def google_auth(data: dict):
    access_token  = data.get("access_token")
    refresh_token = data.get("refresh_token")
    if not access_token:
        return {"status": "error", "message": "Missing token"}
    try:
        user_resp = supabase.auth.get_user(access_token)
        if not user_resp or not user_resp.user:
            return {"status": "error", "message": "Invalid token"}
        u       = user_resp.user
        user_id = u.id
        email   = u.email or ""
        name    = (u.user_metadata or {}).get("full_name", email.split("@")[0])
        avatar  = (u.user_metadata or {}).get("avatar_url", "")
        today   = today_str()
        existing = supabase.table("users").select("*").eq("id", user_id).execute()
        if not existing.data:
            supabase.table("users").insert({
                "id": user_id, "email": email, "name": name,
                "avatar": avatar, "plan": "free_trial",
                "trial_start": today, "day_in_program": 1,
                "streak": 0, "points": 0,
                "tasks_completed": "[]", "proof_wall": "[]",
                "onboarding_done": False, "profile": "{}"
            }).execute()
            user_data = {
                "id": user_id, "email": email, "name": name,
                "plan": "free_trial", "day_in_program": 1,
                "onboarding_done": False
            }
            send_email(email, "Welcome to Zubhai — your 7-day AI sprint starts now",
                email_wrap(f'<div class="tag">Welcome</div><h1>Hey {name}! 7 days to transform how you work.</h1>'
                    f"<p>One question before you start — that's it. No forms. Then straight into Day 1.</p>"
                    f'<div class="card"><p style="margin:0;font-size:13px;color:#666">Day 7 you publish something real. That\'s your AI portfolio.</p></div>'
                    f'<a href="{SITE_URL}" class="btn">Start Now →</a>'
                    f'<p style="font-size:12px;color:#444;margin-top:14px">— Shubh, founder of Zubhai</p>'))
        else:
            user_data = existing.data[0]
        return {"status": "success", "user_id": user_id, "user": user_data}
    except Exception as e:
        print(f"Google auth error: {e}")
        return {"status": "error", "message": str(e)}

# ── EMAIL AUTH ─────────────────────────────────────────────────────────────────
@app.post("/auth/signup")
def signup(data: dict):
    email    = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not email or not password:
        return {"status": "error", "message": "Email and password required"}
    if len(password) < 6:
        return {"status": "error", "message": "Password must be at least 6 characters"}
    try:
        result = supabase.auth.sign_up({"email": email, "password": password})
        if not result.user:
            return {"status": "error", "message": "Signup failed"}
        user_id = result.user.id
        today   = today_str()
        name    = email.split("@")[0]
        try:
            supabase.table("users").insert({
                "id": user_id, "email": email, "name": name,
                "plan": "free_trial", "trial_start": today,
                "day_in_program": 1, "streak": 0, "points": 0,
                "tasks_completed": "[]", "proof_wall": "[]",
                "onboarding_done": False, "profile": "{}"
            }).execute()
        except Exception as e:
            print(f"Insert warning: {e}")
        send_email(email, "Welcome to Zubhai — answer one question to begin",
            email_wrap(f'<div class="tag">Welcome</div><h1>Hey {name}! One question, then Day 1.</h1>'
                f"<p>No lengthy forms. Just tell us where you are and where you want to go. 2 sentences.</p>"
                f'<a href="{SITE_URL}" class="btn">Start Now →</a>'
                f'<p style="font-size:12px;color:#444;margin-top:14px">— Shubh, founder of Zubhai</p>'))
        return {"status": "success", "user_id": user_id,
                "user": {"id": user_id, "email": email, "plan": "free_trial",
                         "day_in_program": 1, "onboarding_done": False}}
    except Exception as e:
        err = str(e)
        if "already" in err.lower():
            return {"status": "error", "message": "Email already registered. Please login."}
        return {"status": "error", "message": err}

@app.post("/auth/login")
def login(data: dict):
    email    = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not email or not password:
        return {"status": "error", "message": "Email and password required"}
    try:
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if not result.user:
            return {"status": "error", "message": "Login failed"}
        user_id = result.user.id
        today   = today_str()
        row     = supabase.table("users").select("*").eq("id", user_id).execute()
        if not row.data:
            supabase.table("users").insert({
                "id": user_id, "email": email, "name": email.split("@")[0],
                "plan": "free_trial", "trial_start": today,
                "day_in_program": 1, "streak": 0, "points": 0,
                "tasks_completed": "[]", "proof_wall": "[]",
                "onboarding_done": False, "profile": "{}"
            }).execute()
            user_data = {"id": user_id, "email": email, "plan": "free_trial",
                         "day_in_program": 1, "onboarding_done": False}
        else:
            user_data = row.data[0]
        return {"status": "success", "user_id": user_id, "user": user_data}
    except Exception as e:
        err = str(e)
        if "Invalid login" in err:
            return {"status": "error", "message": "Wrong email or password"}
        return {"status": "error", "message": err}

@app.get("/auth/user/{user_id}")
def get_user_route(user_id: str):
    row = supabase.table("users").select("*").eq("id", user_id).execute()
    if not row.data:
        return {"status": "error", "message": "User not found"}
    return {"status": "success", "user": row.data[0]}


# ── OTP AUTH ───────────────────────────────────────────────────────────────────
@app.post("/auth/send-otp")
def send_otp(data: dict):
    email = data.get("email", "").strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return {"status": "error", "message": "Enter a valid email"}
    try:
        supabase.auth.sign_in_with_otp({"email": email, "options": {"should_create_user": True}})
        return {"status": "success", "message": "6-digit OTP sent to " + email}
    except Exception as e:
        print(f"Send OTP error: {e}")
        return {"status": "error", "message": "Could not send OTP. Try again."}

@app.post("/auth/verify-otp")
def verify_otp(data: dict):
    email = data.get("email", "").strip().lower()
    token = re.sub(r"\D", "", data.get("token", ""))
    if not email or not token:
        return {"status": "error", "message": "Email and OTP required"}
    if len(token) != 6:
        return {"status": "error", "message": "Enter the 6-digit OTP"}
    try:
        result = supabase.auth.verify_otp({"email": email, "token": token, "type": "email"})
        if not result.user:
            return {"status": "error", "message": "Invalid or expired OTP"}
        user_id  = result.user.id
        today    = today_str()
        name     = email.split("@")[0]
        existing = supabase.table("users").select("*").eq("id", user_id).execute()
        is_new   = not existing.data
        if is_new:
            try:
                supabase.table("users").insert({
                    "id": user_id, "email": email, "name": name,
                    "plan": "free_trial", "trial_start": today,
                    "day_in_program": 1, "streak": 0, "points": 0,
                    "tasks_completed": "[]", "proof_wall": "[]",
                    "onboarding_done": False, "profile": "{}"
                }).execute()
            except Exception as ins_err:
                print(f"OTP insert warning: {ins_err}")
            send_email(email, "Welcome to Zubhai — your 7-day AI sprint starts now",
                email_wrap(f'<div class="tag">Welcome</div><h1>Hey {name}! One question, then Day 1.</h1>'
                    f"<p>Tell us your goal in 2 sentences. Arjun builds your 7-day sprint around it.</p>"
                    f'<a href="{SITE_URL}" class="btn">Start Now →</a>'
                    f'<p style="font-size:12px;color:#444;margin-top:14px">— Shubh, founder of Zubhai</p>'))
            user_data = {"id": user_id, "email": email, "name": name,
                         "plan": "free_trial", "day_in_program": 1, "onboarding_done": False}
        else:
            user_data = existing.data[0]
        return {"status": "success", "user_id": user_id, "user": user_data, "is_new": is_new}
    except Exception as e:
        err = str(e)
        print(f"Verify OTP error: {err}")
        if "invalid" in err.lower() or "expired" in err.lower():
            return {"status": "error", "message": "Wrong or expired OTP. Check your inbox."}
        return {"status": "error", "message": "Verification failed. Try again."}

# ── SMART ONBOARDING ───────────────────────────────────────────────────────────
@app.post("/onboard/parse")
def parse_onboarding(data: dict):
    user_id = data.get("user_id")
    answer  = data.get("answer", "").strip()
    if not user_id or not answer:
        return {"status": "error", "message": "Missing data"}

    parse_prompt = f"""A user signed up for a 7-day AI skills program. They answered this onboarding question:
"In 2-3 sentences — what's your current situation and what do you want to achieve with AI in the next 7 days?"
Their answer: "{answer}"
Extract a structured profile. Return ONLY valid JSON, nothing else:
{{
  "track": "<student|developer|marketing|sales — pick the best fit>",
  "skill_level": "<beginner|intermediate|advanced>",
  "current_role": "<their role in 3-5 words>",
  "goal": "<their main goal in 1 sentence>",
  "tools_known": ["<tools they already use>"],
  "tools_to_learn": ["<tools they explicitly want to learn>"],
  "current_project": "<any project they mentioned, or empty string>",
  "pain_point": "<their #1 frustration, inferred if not explicit>",
  "industry": "<their industry>",
  "timeline": "<urgent|flexible|exploring>",
  "language": "<English|Hindi|Marathi — infer from answer style, default English>"
}}"""

    try:
        r = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": parse_prompt}],
            temperature=0.1, max_tokens=400
        )
        profile = extract_json(r.choices[0].message.content)
        if not profile:
            profile = {**DEFAULT_PROFILE, "raw_answer": answer}
    except Exception as e:
        print(f"Profile parse error: {e}")
        profile = {**DEFAULT_PROFILE, "raw_answer": answer}

    profile["raw_answer"] = answer
    track = profile.get("track", "student")
    field_map = {"student": "student", "developer": "developer", "marketing": "marketing", "sales": "sales"}
    field = field_map.get(track, "student")

    supabase.table("users").update({
        "field": field, "level": profile.get("skill_level", "beginner"),
        "language": profile.get("language", "English"),
        "profile": json.dumps(profile), "onboarding_done": True, "day_in_program": 1,
    }).eq("id", user_id).execute()

    return {
        "status": "success", "profile": profile, "field": field, "track": track,
        "message": build_onboard_confirmation(profile),
    }

def build_onboard_confirmation(profile: dict) -> str:
    track   = profile.get("track", "student")
    level   = profile.get("skill_level", "beginner")
    goal    = profile.get("goal", "")
    tools_k = profile.get("tools_known", [])
    level_line = {
        "beginner":     "Starting from zero is fine — everyone here does.",
        "intermediate": f"You already know {', '.join(tools_k[:2]) if tools_k else 'a few tools'} — we're going to make you dangerous with them.",
        "advanced":     "You've already got the base — this is about speed, systems, and output quality.",
    }.get(level, "")
    track_line = {
        "student":   "Your 7 days are about making your coursework, career prep, and output look 5 years ahead of your batch.",
        "developer": "Your 7 days are about shipping code faster, reading codebases instantly, and adding AI features that impress anyone.",
        "marketing": "Your 7 days are about producing a month of content in one sitting, writing copy that actually converts, and building campaigns in an hour.",
        "sales":     "Your 7 days are about finding qualified leads faster, writing outreach that gets replies, and closing with less friction.",
    }.get(track, "")
    goal_line = f"Your goal: {goal}. We'll get there." if goal else ""
    return f"{level_line} {track_line} {goal_line} Let's start Day 1."

@app.post("/onboard")
def onboard(data: dict):
    user_id      = data.get("user_id")
    field        = data.get("field", "")
    level        = data.get("level", "beginner")
    language     = data.get("language", "English")
    time_per_day = data.get("time_per_day", 15)
    if not user_id or not field:
        return {"status": "error", "message": "Missing data"}
    supabase.table("users").update({
        "field": field, "level": level, "language": language,
        "time_per_day": time_per_day, "onboarding_done": True
    }).eq("id", user_id).execute()
    return {"status": "success"}

# ── THREAT SCORE ───────────────────────────────────────────────────────────────
@app.get("/threat-score/{field}")
def threat_score(field: str):
    f    = field.lower()
    data = THREAT_DATA.get(f, THREAT_DATA.get("student"))
    return {"status": "success", "data": data}

@app.get("/daily-dispatch/{field}")
def daily_dispatch(field: str):
    f  = field.lower()
    td = THREAT_DATA.get(f, THREAT_DATA.get("student"))
    return {"status": "success", "dispatch": td.get("dispatch", "AI is reshaping every profession.")}

# ── MAIN CHAT ENGINE ───────────────────────────────────────────────────────────
@app.post("/chat")
async def chat(data: dict):
    user_id  = data.get("user_id")
    message  = data.get("message", "").strip()
    day      = int(data.get("day", 1))
    field    = data.get("field", "student")
    language = data.get("language", "English")
    history  = data.get("history", [])

    if not user_id or not message:
        return JSONResponse({"status": "error", "message": "Missing data"})

    u = get_user(user_id)
    if not u:
        return JSONResponse({"status": "error", "message": "User not found"})

    today   = today_str()
    plan    = u.get("plan", "free_trial")
    profile = get_profile(u)
    f       = field.lower()
    program = PROGRAM.get(f, PROGRAM["student"])
    day_idx = min(max(day - 1, 0), len(program) - 1)
    day_info = program[day_idx]
    threat  = THREAT_DATA.get(f, THREAT_DATA["student"])
    daily_news = fetch_daily_news(f, profile)

    is_start      = message.startswith("START_SESSION_DAY_")
    msg_lower     = message.lower()
    is_submission = any(x in msg_lower for x in [
        "http", "github", "linkedin", "drive.google", "docs.google",
        "pastebin", "gist", "notion", "paste", "here is", "here's",
        "i built", "i made", "i created", "i wrote", "done", "completed",
        "finished", "check this", "review this", "my code", "```"
    ])

    msg_type             = "code" if f == "developer" else "chat"
    model_name, provider = pick_model(f, day, msg_type)

    prev_days_context = ""
    if day > 1:
        prev_titles       = [program[i]["title"] for i in range(min(day_idx, len(program)))]
        prev_days_context = "Days done: " + " → ".join(prev_titles[:day_idx])

    next_day_preview = ""
    if day_idx + 1 < len(program):
        next_day_preview = f"Next up (Day {day+1}): {program[day_idx+1]['title']}"

    pers = build_personalization_context(profile, day_info, f, day)

    # ── GET JOURNEY HISTORY + GENERATE PROMPT ON SESSION START ────────────────
    journey_history = get_journey_history(user_id, limit=10)
    collective_ctx  = get_collective_patterns(f, day)

    generated_prompt = ""
    if is_start:
        generated_prompt = generate_task_prompt(
            profile, day_info, f, day, journey_history
        )

    # Build journey context for system prompt
    journey_summary = ""
    if journey_history:
        recent = journey_history[:3]
        lines = []
        for j in recent:
            lines.append(
                f"Day {j['day']} ({j.get('task_title','')}) — "
                f"score {j.get('score',0)}/10"
                + (f" — struggled: {j.get('where_stuck','')}" if j.get('where_stuck') else "")
                + (f" — insight: {j.get('ai_insight','')}" if j.get('ai_insight') else "")
            )
        journey_summary = "\n".join(lines)

    # Grade calibration (same as before)
    if day <= 2:
        grade_calibration = f"""GRADING Day {day} (EARLY): Score 7-9/10 for genuine attempt. 1 sentence good, 1 sentence improve. Encouraging."""
    elif day <= 4:
        grade_calibration = f"""GRADING Day {day} (BUILDING): Score 6-8/10. Push for specificity. 2 sentences feedback."""
    else:
        grade_calibration = f"""GRADING Day {day} (ADVANCED): Full range 4-10. Real standards. 3 sentences. Honest."""

    system = f"""You are Arjun — mentor at Zubhai (zubhai.com). ⚡
Never say you're an AI. Blunt, specific, zero corporate BS.
TODAY — Day {day}/7: {day_info['title']}
{prev_days_context}
{next_day_preview}
Language: {u.get('language', language)}

USER PROFILE:
{pers}

USER'S FULL JOURNEY (use this — don't repeat what they've already done):
{journey_summary if journey_summary else "First session."}

COLLECTIVE INSIGHT (what similar users struggled with here):
{collective_ctx if collective_ctx else "Not enough data yet."}

CHARACTER: Older cousin in AI. Real India examples. Short. Punchy.
Never "Great!" or "Sure!" or "Of course!"
7 days = intro sprint. Never say "master this in 7 days."

══════════════════════════════════════
SESSION START:
══════════════════════════════════════
{"GENERATED PROMPT FOR THIS USER:" + chr(10) + generated_prompt if is_start and generated_prompt else ""}

When is_start:
→ 1 punchy line: why today matters FOR THEM specifically (use their journey)
→ Show the generated prompt in this EXACT format:

---
**Your task today:** [2 lines max]

**Copy this into {day_info.get('tool','Claude')}:**
[COPY_PROMPT_START]
{generated_prompt if generated_prompt else "[prompt will appear here]"}
[COPY_PROMPT_END]

**Steps:**
1. Go to [tool URL]
2. Paste the prompt — it will ask you questions
3. Answer them honestly
4. Paste the final output back here

When done → paste your output here and I grade it.
---

══════════════════════════════════════
SUBMISSION:
══════════════════════════════════════
{grade_calibration}
→ Extract WHERE they got stuck (for memory storage)
→ Note any breakthrough moment
→ End with:
ZUBHAI_GRADE:{{"score":{{"n":SCORE,"good":"specific praise","improve":"specific fix","day":{day},"field":"{f}","where_stuck":"[what confused them]","breakthrough":"[moment they got it if any]"}}}}

QUESTIONS: 2 sentences max. "now back to it."
LIVE NEWS: {daily_news.get('highlights', [daily_news['headline']])}
NEVER repeat yourself. SHORT always except starter or feedback."""

    # URL fetching (same as before)
    fetched_url_content = ""
    url_match = re.search(r'https?://\S+', message)
    if url_match and not is_start:
        url = url_match.group(0)
        # Detect AI share links — can't be fetched
        ai_share_patterns = ["chatgpt.com/s/", "claude.ai/share/", "chat.openai.com/share/"]
        is_ai_share = any(p in url for p in ai_share_patterns)
        if is_ai_share:
            fetched_url_content = f"[AI SHARE LINK DETECTED: {url}] — Cannot read this link directly. User shared their AI conversation as proof."
        else:
            try:
                res = requests.get(f"https://r.jina.ai/{url}", timeout=10)
                if res.status_code == 200 and len(res.text) > 80:
                    fetched_url_content = res.text[:3000]
            except:
                pass

    messages = [{"role": m["role"], "content": m["content"]} for m in history[-16:]]

    if is_start:
        actual_msg = "Give me today's task now."
    elif fetched_url_content:
        actual_msg = f"{message}\n\n[URL CONTENT]:\n{fetched_url_content}"
    else:
        actual_msg = message

    messages.append({"role": "user", "content": actual_msg})

    async def generate():
        full_text = ""
        try:
            if provider == "claude":
                with claude_client.messages.stream(
                    model=model_name, max_tokens=700,
                    system=system, messages=messages
                ) as stream:
                    for text in stream.text_stream:
                        full_text += text
                        yield f"data: {json.dumps({'text': text})}\n\n"
            else:
                stream = openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "system", "content": system}] + messages,
                    max_tokens=700, temperature=0.7, stream=True
                )
                for chunk in stream:
                    text = chunk.choices[0].delta.content or ""
                    if text:
                        full_text += text
                        yield f"data: {json.dumps({'text': text})}\n\n"

            supabase.table("users").update({"last_active": today}).eq("id", user_id).execute()

            # ── PARSE GRADE + STORE JOURNEY ────────────────────────────────
            grade_data  = None
            share_post  = None
            points_earn = 0

            if "ZUBHAI_GRADE:" in full_text:
                try:
                    grade_raw  = full_text.split("ZUBHAI_GRADE:")[1].strip()
                    start_i    = grade_raw.find("{")
                    end_i      = grade_raw.rfind("}") + 1
                    grade_data = json.loads(grade_raw[start_i:end_i])
                    score_obj  = grade_data.get("score", {})
                    score      = int(score_obj.get("n", 0)) if isinstance(score_obj, dict) else int(grade_data.get("n", 0))
                    where_stuck   = score_obj.get("where_stuck", "") if isinstance(score_obj, dict) else ""
                    breakthrough  = score_obj.get("breakthrough", "") if isinstance(score_obj, dict) else ""
                    pts           = score * 15
                    new_pts       = (u.get("points") or 0) + pts
                    points_earn   = pts

                    already_done = has_completed_day(u, day)
                    new_day      = u.get("day_in_program") or 1
                    if not already_done:
                        new_day = min(new_day + 1, 8)

                    # ── STORE IN JOURNEY TABLE ─────────────────────────────
                    user_output_text = ""
                    for m in reversed(history[-10:]):
                        if m["role"] == "user" and len(m["content"]) > 80:
                            user_output_text = m["content"]
                            break

                    store_journey(
                        user_id     = user_id,
                        day         = day,
                        field       = f,
                        task_title  = day_info["title"],
                        prompt_generated = generated_prompt or data.get("last_generated_prompt", ""),
                        user_output = user_output_text,
                        score       = score,
                        where_stuck = where_stuck,
                        breakthrough = breakthrough,
                        iterations  = max(1, sum(1 for m in history if m["role"] == "user"))
                    )

                    # Update users table
                    tasks_completed = []
                    try:
                        tc = u.get("tasks_completed", "[]")
                        tasks_completed = json.loads(tc) if isinstance(tc, str) else (tc or [])
                    except:
                        tasks_completed = []

                    if not already_done:
                        tasks_completed.append({
                            "day": day, "title": day_info["title"],
                            "score": score, "points": pts,
                            "field": f, "completed_at": today_str()
                        })

                    supabase.table("users").update({
                        "points": new_pts,
                        "day_in_program": new_day,
                        "last_active": today,
                        "streak": (u.get("streak") or 0) + 1,
                        "tasks_completed": json.dumps(tasks_completed)
                    }).eq("id", user_id).execute()

                    # Share post generation (same as before)
                    if score >= 6:
                        what_good = score_obj.get("good", "") if isinstance(score_obj, dict) else ""
                        post_prompt = f"""Write a LinkedIn/Twitter post. 3-4 lines.
Person finished Day {day}/7 intro sprint on Zubhai. Field: {field}.
Built: {day_info['title']}. Score: {score}/10. {what_good}
Line 1: specific thing they built
Line 2: one real insight
Line 3: "Day {day}/7 done ⚡ zubhai.com"
Line 4: #LearnAI #Zubhai
Sound human. Zero humble-brag. Return ONLY post text."""
                        try:
                            pr = openai_client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": post_prompt}],
                                max_tokens=120, temperature=0.8
                            )
                            share_post = pr.choices[0].message.content.strip()
                        except:
                            share_post = f"⚡ Day {day} done on Zubhai.\n{day_info['title']} — {score}/10.\nzubhai.com #LearnAI"

                    # Milestone check for chat grading
                    chat_milestone = MILESTONES.get(day)
                    if chat_milestone and not has_completed_day(u, day):
                        try:
                            email_addr = u.get("email", "")
                            uname = u.get("name", email_addr.split("@")[0])
                            send_milestone_email(email_addr, uname, chat_milestone)
                        except Exception as me:
                            print(f"Chat milestone email error: {me}")

                    yield f"data: {json.dumps({'done': True, 'grade': grade_data, 'share_post': share_post, 'points_earned': points_earn, 'milestone': chat_milestone})}\n\n"
                    return
                except Exception as ge:
                    print(f"Grade parse error: {ge}")

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            print(f"Chat stream error: {e}")
            yield f"data: {json.dumps({'error': 'Service error. Try again.'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive",
                 "X-Accel-Buffering": "no", "Access-Control-Allow-Origin": "*"})


# ── JOURNEY READ ENDPOINT ──────────────────────────────────────────────────────
@app.get("/journey/{user_id}")
def get_user_journey(user_id: str):
    history = get_journey_history(user_id, limit=20)
    return {"status": "success", "journey": history}

# ── TASK SUBMISSION & VERIFICATION ────────────────────────────────────────────
@app.post("/submit-task")
def submit_task(data: dict):
    user_id    = data.get("user_id")
    day        = int(data.get("day", 1))
    field      = data.get("field", "student")
    proof_url  = data.get("proof_url", "").strip()
    proof_text = data.get("proof_text", "").strip()

    if not user_id:
        return {"status": "error", "message": "Missing user_id"}

    u = get_user(user_id)
    if not u:
        return {"status": "error", "message": "User not found"}

    profile  = get_profile(u)
    f        = field.lower()
    program  = PROGRAM.get(f, PROGRAM["student"])
    day_idx  = min(max(day - 1, 0), len(program) - 1)
    day_info = program[day_idx]

    submitted_content = proof_text
    url_readable      = False
    if proof_url:
        try:
            res = requests.get(f"https://r.jina.ai/{proof_url}", timeout=15)
            if res.status_code == 200 and len(res.text) > 80:
                submitted_content = res.text[:3000]
                url_readable      = True
        except:
            pass
        if not url_readable:
            submitted_content = f"URL submitted: {proof_url}. Content could not be read automatically."

    if not submitted_content:
        return {"status": "error", "message": "Please provide a URL or describe what you did"}

    is_day7 = (day == 7)
    level   = profile.get("skill_level", "beginner")

    if day <= 2:
        grade_standard = "This is Day 1-2. Grade generously — 7-9/10 for any genuine attempt. Feedback: 1 positive, 1 actionable improvement. Be encouraging."
    elif day <= 4:
        grade_standard = "Day 3-4. Moderate standard — 6-8/10. Push for specificity but keep it positive."
    else:
        grade_standard = f"Day {day}. Full standards. Generic = 4-5/10. Specific, real work = 7-9/10. Milestone Day 7: must be published, real work."

    grade_prompt = f"""Grade this AI learning task submission.
TASK: {day_info['task']}
WHAT WAS REQUIRED: {day_info['verify']}
USER LEVEL: {level}
SUBMITTED: {submitted_content}
GRADING STANDARD: {grade_standard}
{"DAY 7 MILESTONE: Grade strictly — must be published, public, real work." if is_day7 else ""}
Return ONLY JSON:
{{"score": 7, "points": 105, "feedback": "2 sentence specific feedback", "what_was_good": "one specific thing done well", "what_to_improve": "one actionable improvement", "milestone_worthy": false}}"""

    result = None
    try:
        r = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": grade_prompt}],
            temperature=0.2, max_tokens=300
        )
        result = extract_json(r.choices[0].message.content)
    except Exception as e:
        print(f"Grade error: {e}")

    if not result:
        result = {"score": 7, "points": 105, "feedback": "Submitted. Good start.",
                  "what_was_good": "You showed up and did the work",
                  "what_to_improve": "Add more detail next time",
                  "milestone_worthy": False}

    score      = max(1, min(10, int(result.get("score", 7))))
    points     = score * 15
    new_points = (u.get("points") or 0) + points
    new_day    = min((u.get("day_in_program") or 1) + 1, 8)

    proof_wall = []
    try:
        pw         = u.get("proof_wall", "[]")
        proof_wall = json.loads(pw) if isinstance(pw, str) else (pw or [])
    except:
        proof_wall = []

    tasks_completed = []
    try:
        tc              = u.get("tasks_completed", "[]")
        tasks_completed = json.loads(tc) if isinstance(tc, str) else (tc or [])
    except:
        tasks_completed = []

    task_entry = {
        "day": day, "title": day_info["title"], "score": score,
        "points": points, "proof_url": proof_url, "field": field,
        "completed_at": today_str()
    }
    tasks_completed.append(task_entry)

    if is_day7 and result.get("milestone_worthy", score >= 6) and proof_url:
        proof_wall.append({
            "day": day, "title": day_info["title"], "url": proof_url,
            "field": field, "score": score, "date": today_str()
        })

    supabase.table("users").update({
        "points": new_points, "day_in_program": new_day,
        "streak": (u.get("streak") or 0) + 1,
        "tasks_completed": json.dumps(tasks_completed),
        "proof_wall": json.dumps(proof_wall),
        "last_active": today_str()
    }).eq("id", user_id).execute()

    # ── EMAILS: task complete + milestone ────────────────────────────────────
    try:
        name = u.get("name", u.get("email", "").split("@")[0])
        email_addr = u.get("email", "")
        # Task completion email
        send_email(email_addr, f"Day {day} done — {score}/10",
            email_wrap(f'<div class="tag">Day {day} Complete</div>'
                f"<h1>You scored {score}/10</h1>"
                f'<div class="card"><p style="margin:0;font-size:13px;color:#888">{result.get("feedback", "")}</p></div>'
                f"<p style='color:#e8602c;font-size:14px;margin:0'>+{points} points</p>"
                f'<a href="{SITE_URL}" class="btn">Continue to Day {min(day+1,7)} →</a>'))
        # Milestone email (days 3, 5, 7)
        milestone = MILESTONES.get(day)
        if milestone:
            send_milestone_email(email_addr, name, milestone)
    except Exception as e:
        print(f"Score/milestone email error: {e}")

    # Check milestone for frontend popup
    milestone_data = MILESTONES.get(day)

    return {
        "status": "success", "score": score, "points": points,
        "total_points": new_points, "feedback": result.get("feedback", ""),
        "what_was_good": result.get("what_was_good", ""),
        "what_to_improve": result.get("what_to_improve", ""),
        "next_day": new_day, "is_milestone": is_day7 or bool(milestone_data),
        "milestone": milestone_data,
        "added_to_proof_wall": is_day7 and bool(proof_url)
    }

# ── PROOF WALL ─────────────────────────────────────────────────────────────────
@app.get("/proof-wall/{user_id}")
def proof_wall(user_id: str):
    u = get_user(user_id)
    if not u:
        return {"status": "error", "message": "User not found"}
    pw = []
    try:
        raw = u.get("proof_wall", "[]")
        pw  = json.loads(raw) if isinstance(raw, str) else (raw or [])
    except:
        pw = []
    return {
        "status": "success",
        "name": u.get("name", u.get("email", "").split("@")[0]),
        "field": u.get("field", ""),
        "points": u.get("points", 0),
        "proof_wall": pw,
        "tasks_completed": len(json.loads(u.get("tasks_completed", "[]"))
            if isinstance(u.get("tasks_completed"), str)
            else u.get("tasks_completed") or [])
    }

# ── LEADERBOARD ────────────────────────────────────────────────────────────────
@app.get("/leaderboard")
def leaderboard():
    result = supabase.table("users").select(
        "email, name, points, field, streak, day_in_program, plan"
    ).order("points", desc=True).limit(100).execute()
    rows = []
    for u in (result.data or []):
        rows.append({
            "name":           u.get("name") or (u.get("email","").split("@")[0]),
            "points":         u.get("points") or 0,
            "field":          u.get("field") or "—",
            "streak":         u.get("streak") or 0,
            "day_in_program": u.get("day_in_program") or 1,
            "plan":           u.get("plan") or "free_trial",
        })
    return {"leaderboard": rows, "total": len(rows)}

# ── UPGRADE INTENT ─────────────────────────────────────────────────────────────
@app.post("/upgrade")
def upgrade_intent(data: dict):
    user_id = data.get("user_id")
    plan    = data.get("plan", "pro")
    if not user_id:
        return {"status": "error"}
    u = get_user(user_id)
    if u:
        send_email(SENDER_EMAIL,
            f"🔥 Upgrade intent: {u.get('email')} wants {plan}",
            email_wrap(f"<p>User <strong>{u.get('email')}</strong> clicked upgrade to <strong>{plan}</strong>.</p>"
                       f"<p>Field: {u.get('field')} | Points: {u.get('points')} | Day: {u.get('day_in_program')}</p>"
                       f"<p>Profile: {u.get('profile', 'none')}</p>"))
    return {"status": "success", "message": "Upgrade noted — Shubh will contact you within 24hrs with payment link"}

# ── ADMIN ──────────────────────────────────────────────────────────────────────
@app.get("/admin/stats")
def admin_stats(secret: str = ""):
    if secret != ADMIN_SECRET:
        return {"status": "error", "message": "Unauthorized"}
    total     = supabase.table("users").select("id", count="exact").execute()
    onboarded = supabase.table("users").select("id", count="exact").eq("onboarding_done", True).execute()
    active    = supabase.table("users").select("id", count="exact").gt("points", 0).execute()
    pro       = supabase.table("users").select("id", count="exact").eq("plan", "pro").execute()
    max_plan  = supabase.table("users").select("id", count="exact").eq("plan", "max").execute()
    return {
        "total_users": total.count,
        "onboarded": onboarded.count,
        "active_users": active.count,
        "pro_users": pro.count,
        "max_users": max_plan.count,
    }

@app.post("/admin/set-plan")
def set_plan(data: dict):
    if data.get("secret") != ADMIN_SECRET:
        return {"status": "error", "message": "Unauthorized"}
    user_id = data.get("user_id")
    plan    = data.get("plan")
    if not user_id or plan not in PLAN_LIMITS:
        return {"status": "error", "message": "Invalid"}
    supabase.table("users").update({"plan": plan}).eq("id", user_id).execute()
    return {"status": "success"}

@app.post("/submit-feedback")
def submit_feedback(data: dict):
    try:
        supabase.table("feedback").insert({
            "name": data.get("name", ""), "field": data.get("field", ""),
            "message": data.get("message", "")
        }).execute()
    except Exception as e:
        print(f"Feedback: {e}")
    return {"status": "received"}

# ══════════════════════════════════════════════════════════════════════════════
# MISSING ENDPOINTS — added to fix 404s
# ══════════════════════════════════════════════════════════════════════════════

# ── USAGE (called by frontend loadUsage()) ─────────────────────────────────────
@app.get("/usage/{user_id}")
def get_usage(user_id: str):
    """Returns session usage, plan info, and reset timer for the sidebar meter."""
    u = get_user(user_id)
    if not u:
        return {"status": "error", "message": "User not found"}

    plan  = u.get("plan", "free_trial")
    today = date.today().isoformat()

    # Count messages sent today from usage_log if it exists, else fallback to 0
    msgs_today = 0
    try:
        res = supabase.table("usage_log") \
            .select("id", count="exact") \
            .eq("user_id", user_id) \
            .eq("date", today) \
            .execute()
        msgs_today = res.count or 0
    except Exception:
        msgs_today = 0  # table may not exist yet — safe default

    # Plan limits
    limits = {"free_trial": 5, "pro": 50, "max": 999}
    session_limit = limits.get(plan, 5)
    msgs_left     = max(0, session_limit - msgs_today)

    # Seconds until midnight IST (UTC+5:30)
    from datetime import timezone
    now_utc   = datetime.now(timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist   = now_utc + ist_offset
    midnight_ist = (now_ist + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    reset_seconds = int((midnight_ist - now_ist).total_seconds())

    # Trial expiry check
    trial_expired = False
    if plan == "free_trial":
        try:
            start = date.fromisoformat(u.get("trial_start") or today)
            trial_expired = (date.today() - start).days >= 7
        except Exception:
            pass

    return {
        "status":        "success",
        "plan":          plan,
        "msgs_today":    msgs_today,
        "msgs_left":     msgs_left,
        "sessions_left": msgs_left,
        "sessions_limit": session_limit,
        "msgs_limit":    session_limit,
        "reset_seconds": reset_seconds,
        "trial_expired": trial_expired,
    }

# ── WAITLIST ───────────────────────────────────────────────────────────────────
@app.post("/waitlist")
def waitlist(data: dict):
    email = data.get("email", "").strip()
    name  = data.get("name", "").strip()
    if not email:
        return {"status": "error", "message": "Email required"}
    try:
        supabase.table("waitlist").insert({
            "email": email, "name": name, "created_at": date.today().isoformat()
        }).execute()
    except Exception as e:
        print(f"Waitlist insert: {e}")
    try:
        resend.Emails.send({
            "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
            "to":   [email],
            "subject": "You're on the Zubhai waitlist 🔥",
            "html": f"<p>Hey {name or 'there'}! You're on the list. Shubh will reach out when your spot opens.</p>"
        })
    except Exception as e:
        print(f"Waitlist email: {e}")
    return {"status": "success", "message": "You're on the list!"}

# Newsletter alias
@app.post("/newsletter")
def newsletter(data: dict):
    return waitlist(data)

# ── ONBOARD SAVE TURN ──────────────────────────────────────────────────────────
@app.post("/onboard/save-turn")
def save_onboard_turn(data: dict):
    """Persist each onboarding chat message so data survives page refresh."""
    user_id = data.get("user_id")
    role    = data.get("role")
    content = data.get("content", "").strip()
    if not user_id or not role or not content:
        return {"status": "error"}
    u = get_user(user_id)
    if not u:
        return {"status": "error"}
    try:
        raw        = u.get("onboard_transcript") or "[]"
        transcript = json.loads(raw) if isinstance(raw, str) else (raw or [])
        if not isinstance(transcript, list):
            transcript = []
    except Exception:
        transcript = []
    transcript.append({
        "role": role, "content": content,
        "ts": datetime.now().isoformat()
    })
    transcript = transcript[-40:]
    supabase.table("users").update({
        "onboard_transcript": json.dumps(transcript)
    }).eq("id", user_id).execute()
    return {"status": "success", "turns": len(transcript)}

# ── ONBOARD TRANSCRIPT (resume after refresh) ──────────────────────────────────
@app.get("/onboard/transcript/{user_id}")
def get_onboard_transcript(user_id: str):
    u = get_user(user_id)
    if not u:
        return {"status": "error"}
    try:
        transcript = json.loads(u.get("onboard_transcript") or "[]")
    except Exception:
        transcript = []
    return {
        "status":         "success",
        "transcript":     transcript,
        "onboarding_done": u.get("onboarding_done", False)
    }

# ── PROFILE NUDGE ──────────────────────────────────────────────────────────────
PROFILE_NUDGES_LIST = [
    {"key": "company",          "question": "Which company or college are you at?",              "placeholder": "e.g., TCS / IIT Bombay / Freelance"},
    {"key": "desired_role",     "question": "What role are you targeting in the next 6–12 months?", "placeholder": "e.g., Senior Engineer / Product Manager"},
    {"key": "experience_years", "question": "How many years of experience do you have?",         "placeholder": "e.g., 2 / Fresher"},
    {"key": "main_kpi",         "question": "What's the one KPI you most want AI to improve?",  "placeholder": "e.g., Ship PRs faster / Improve CTR"},
    {"key": "biggest_blocker",  "question": "What's your biggest blocker right now?",           "placeholder": "e.g., No time / Don't know where to start"},
    {"key": "learning_style",   "question": "How do you learn best?",                           "placeholder": "e.g., Hands-on projects / Reading"},
]

@app.get("/profile/nudge/{user_id}")
def profile_nudge(user_id: str):
    u = get_user(user_id)
    if not u:
        return {"status": "error", "message": "User not found"}
    try:
        raw     = u.get("profile") or "{}"
        profile = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        profile = {}
    for n in PROFILE_NUDGES_LIST:
        if not str(profile.get(n["key"], "")).strip():
            return {"status": "success", "nudge": n, "completed": False}
    return {"status": "success", "completed": True}

@app.post("/profile/update")
def profile_update(data: dict):
    user_id = data.get("user_id")
    updates = data.get("updates", {})
    if not user_id or not isinstance(updates, dict):
        return {"status": "error", "message": "Missing data"}
    u = get_user(user_id)
    if not u:
        return {"status": "error", "message": "User not found"}
    try:
        raw     = u.get("profile") or "{}"
        profile = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        profile = {}
    profile.update({k: v for k, v in updates.items() if v not in (None, "")})
    supabase.table("users").update({
        "profile": json.dumps(profile)
    }).eq("id", user_id).execute()
    return {"status": "success", "profile": profile}


# ── PROOF SCREENSHOT STORAGE ────────────────────────────────────────────────
@app.post("/proof/screenshot")
def save_proof_screenshot(data: dict):
    """
    Save a screenshot to the user's proof wall.
    Stores base64 image data directly in Supabase (screenshots table).
    Also triggers Arjun analysis if day >= 2.
    """
    user_id     = data.get("user_id")
    day         = int(data.get("day", 1))
    field       = data.get("field", "student")
    caption     = data.get("caption", "").strip() or f"Day {day} output"
    image_b64   = data.get("image_base64", "")
    image_type  = data.get("image_type", "image/jpeg")

    if not user_id or not image_b64:
        return {"status": "error", "message": "Missing image or user_id"}

    u = get_user(user_id)
    if not u:
        return {"status": "error", "message": "User not found"}

    # Build data URI for display
    screenshot_data = f"data:{image_type};base64,{image_b64}"

    entry = {
        "user_id":         user_id,
        "day":             day,
        "field":           field,
        "caption":         caption,
        "screenshot_data": screenshot_data,
        "date":            date.today().isoformat(),
    }

    try:
        supabase.table("proof_screenshots").insert(entry).execute()
    except Exception as e:
        print(f"Screenshot insert error: {e}")
        # Table may not exist yet — save to user profile JSON as fallback
        try:
            raw       = u.get("profile") or "{}"
            profile   = json.loads(raw) if isinstance(raw, str) else (raw or {})
            shots     = profile.get("screenshots", [])
            shots.append({
                "day": day, "field": field, "caption": caption,
                "date": date.today().isoformat(),
                # Don't store full base64 in profile JSON — too large
                "note": "screenshot saved (table pending)"
            })
            profile["screenshots"] = shots[-20:]  # keep last 20
            supabase.table("users").update({
                "profile": json.dumps(profile)
            }).eq("id", user_id).execute()
        except Exception as e2:
            print(f"Fallback screenshot save error: {e2}")

    # Notify Shubh (for analysis)
    try:
        send_email(
            SENDER_EMAIL,
            f"📸 Screenshot uploaded — Day {day} · {u.get('email','')}",
            email_wrap(
                f"<p><strong>{u.get('name',u.get('email',''))}</strong> uploaded a Day {day} screenshot.</p>"
                f"<p>Field: {field} · Caption: {caption}</p>"
                f"<p>This is for your task analysis — review what they built.</p>"
                f'<img src="{screenshot_data}" style="max-width:100%;border-radius:8px;margin-top:12px" alt="screenshot"/>'
            )
        )
    except Exception as e:
        print(f"Screenshot email error: {e}")

    return {"status": "success", "message": "Screenshot saved to your Proof Wall"}


# ── UPDATE proof-wall endpoint to include screenshots ─────────────────────
# Override the existing proof-wall endpoint to also return screenshots
@app.get("/proof-wall-v2/{user_id}")
def proof_wall_v2(user_id: str):
    u = get_user(user_id)
    if not u:
        return {"status": "error", "message": "User not found"}

    # Proof wall entries
    pw = []
    try:
        raw = u.get("proof_wall", "[]")
        pw  = json.loads(raw) if isinstance(raw, str) else (raw or [])
    except:
        pw = []

    # Screenshots
    screenshots = []
    try:
        res = supabase.table("proof_screenshots") \
            .select("day,field,caption,screenshot_data,date") \
            .eq("user_id", user_id) \
            .order("date", desc=True) \
            .limit(30) \
            .execute()
        screenshots = res.data or []
    except Exception as e:
        print(f"Screenshots fetch error: {e}")

    tasks_completed = 0
    try:
        tc = u.get("tasks_completed", "[]")
        tasks_completed = len(json.loads(tc) if isinstance(tc, str) else (tc or []))
    except:
        pass

    return {
        "status":          "success",
        "name":            u.get("name", u.get("email", "").split("@")[0]),
        "field":           u.get("field", ""),
        "points":          u.get("points", 0),
        "proof_wall":      pw,
        "screenshots":     screenshots,
        "tasks_completed": tasks_completed,
    }
