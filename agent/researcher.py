import logging, time
from datetime import datetime, timedelta
import anthropic, config
from data.competitors import COMPETITOR_DOMAIN_KEYWORDS, DIRECT_COMPETITOR_NAMES, INDIRECT_COMPETITOR_NAMES

logger = logging.getLogger(__name__)

_SEARCH_SYSTEM = """\
You are a competitive intelligence analyst for Atlassian (TEAM), \
the #1 developer and team collaboration platform (Jira, Confluence, Jira Service Management, Bitbucket).

DIRECT competitors: Linear, GitLab, GitHub Projects, Monday.com, Asana, ClickUp, \
Notion, ServiceNow, Smartsheet, Shortcut, Coda, Height.

INDIRECT competitors: Microsoft (Azure DevOps + Loop + GitHub), Salesforce/Slack, \
Figma, AI-native PM tools (Dart, Taskade, Height AI).

For each finding output one line:
FINDING|||[Company]|||[investment|product|metrics|partnership|platform_shift|vc_signal]|||[HIGH|MEDIUM]|||[VC firm or N/A]|||[One sentence description]|||[Source URL]

HIGH: direct competitor funding/product/enterprise win; migration from Jira/Confluence; AI replacing Jira at scale.
MEDIUM: devops/collab SaaS Series B+; ITSM startup lands major customer; VC blog on dev-tooling.
Skip LOW. When done: BLOCK_COMPLETE
"""

def _date_range():
    today = datetime.now()
    return f"{(today - timedelta(days=7)).strftime('%B %d')}-{today.strftime('%B %d, %Y')}"

_SEARCH_BLOCKS = [
    {"name": "direct_competitors", "prompt_template": "Search for news from the past 7 days ({date_range}) about Atlassian direct competitors:\n- Linear: funding, product updates, enterprise wins, AI features\n- GitLab (GTLB): earnings, product launches, customer news, M&A\n- Monday.com (MNDY): earnings, new releases, dev/IT workflow expansion\n- Asana (ASAN): product, funding, AI features, enterprise news\n- ClickUp: funding, product launches, enterprise announcements\n- Notion: funding, enterprise expansion, AI features, wiki news\n- ServiceNow: ITSM features competing with Jira Service Management\n- Shortcut / Coda / Height: funding, product launches, wins\nOutput all HIGH and MEDIUM FINDING||| lines, then: BLOCK_COMPLETE"},
    {"name": "ai_devtools_and_vc", "prompt_template": "Search for news from the past 7 days ({date_range}) about:\nPART A - AI-native dev and team tools:\n- GitHub Copilot Workspace: new features, enterprise adoption, PM expansion\n- Microsoft Loop: Confluence competitor, enterprise rollout\n- Height.app: funding, AI features, enterprise adoption\n- Dart, Taskade: funding, product launches\nPART B - VC investments in developer tooling:\n- Search: Accel OR Sequoia OR Benchmark developer tooling investment 2026\n- Search: General Catalyst OR Insight Partners project management software 2026\n- Search: Bessemer OR Index Ventures devops OR collaboration SaaS 2026\nOutput all HIGH and MEDIUM FINDING||| lines, then: BLOCK_COMPLETE"},
    {"name": "market_signals", "prompt_template": "Search for news from the past 7 days ({date_range}) about broader dev tooling market signals:\n- project management software Series B OR C OR D 2026\n- ITSM platform replaced OR migrated from Jira OR Confluence 2026\n- Atlassian competitor announcement {month_year}\n- enterprise switching from Jira OR replacing Confluence 2026\n- developer productivity platform raised funding 2026\n- VC blog developer tooling investment thesis 2026\nAlso: Guru knowledge base, Tettra wiki, Slite, Slab, Shortcut, Coda news.\nOutput all HIGH and MEDIUM FINDING||| lines, then: BLOCK_COMPLETE"},
]

def _parse_findings(text):
    findings = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("FINDING|||"):
            continue
        parts = line.split("|||")
        if len(parts) < 7:
            continue
        findings.append({"company": parts[1].strip(), "type": parts[2].strip().lower(), "relevance": parts[3].strip().upper(), "vc_firm": parts[4].strip(), "description": parts[5].strip(), "source": parts[6].strip(), "found_at": datetime.now().isoformat()})
    return findings

def _run_block(client, block):
    user_prompt = block["prompt_template"].format(date_range=_date_range(), month_year=datetime.now().strftime("%B %Y"))
    messages = [{"role": "user", "content": user_prompt}]
    accumulated = ""
    continuations = 0
    while continuations <= 3:
        response = client.messages.create(model="claude-sonnet-4-6", max_tokens=1500, system=_SEARCH_SYSTEM, tools=[{"type": "web_search_20260209", "name": "web_search"}], messages=messages)
        for cb in response.content:
            if hasattr(cb, "text"):
                accumulated += cb.text + "\n"
        if response.stop_reason == "end_turn":
            break
        elif response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            continuations += 1
        else:
            break
    return _parse_findings(accumulated)

BLOCK_PAUSE_SECONDS = 15

def run_research():
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, timeout=180.0)
    all_findings = []
    for i, block in enumerate(_SEARCH_BLOCKS):
        logger.info("Search block %d/%d - %s", i + 1, len(_SEARCH_BLOCKS), block["name"])
        try:
            findings = _run_block(client, block)
            all_findings.extend(findings)
            logger.info("  -> %d finding(s)", len(findings))
        except anthropic.RateLimitError:
            logger.warning("Rate limit on '%s' - waiting 60s", block["name"])
            time.sleep(60)
        except Exception as exc:
            logger.error("Block '%s' failed: %s", block["name"], exc)
        if i < len(_SEARCH_BLOCKS) - 1:
            time.sleep(BLOCK_PAUSE_SECONDS)
    seen = set()
    deduped = []
    for f in all_findings:
        key = f"{f['company'].lower()}|{f['type'].lower()}"
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    deduped.sort(key=lambda f: (0 if f.get("relevance") == "HIGH" else 1))
    logger.info("Research complete - %d unique findings", len(deduped))
    return deduped
