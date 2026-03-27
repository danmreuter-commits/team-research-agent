"""Atlassian competitive landscape knowledge base."""

DIRECT_COMPETITOR_NAMES = [
    "linear", "gitlab", "github", "monday.com", "asana", "clickup", "notion",
    "servicenow", "smartsheet", "shortcut", "coda", "height",
]
INDIRECT_COMPETITOR_NAMES = [
    "azure devops", "microsoft loop", "microsoft teams", "slack", "figma",
    "dart", "taskade", "guru", "tettra", "slab", "slite",
]
COMPETITOR_DOMAIN_KEYWORDS = [
    "issue tracking", "project management", "sprint planning", "agile software",
    "ITSM", "IT service management", "knowledge base", "team wiki",
    "developer productivity", "devops platform", "CI/CD pipeline",
    "incident management", "service catalog", "work management",
    "team collaboration", "backlog management", "scrum board", "kanban",
]
ATLASSIAN_CONTEXT = """
ABOUT ATLASSIAN (TEAM):
Products: Jira Software, Jira Service Management, Confluence, Bitbucket, Trello, Opsgenie, Statuspage.
Business model: SaaS per-user. Market position: #1 developer issue tracking and ITSM.

DIRECT COMPETITORS: Linear, GitLab, GitHub, Monday.com, Asana, ClickUp, Notion, ServiceNow, Smartsheet, Shortcut, Coda, Height.
INDIRECT: Microsoft (Azure DevOps + Loop + GitHub), Salesforce/Slack, Figma, Dart, Taskade, Guru, Tettra.
EMERGING THREATS: GitHub Copilot Workspace, Microsoft Loop, Height AI, Notion AI, Linear AI.

HIGH relevance: direct competitor funding/product/enterprise win; migration away from Jira/Confluence; AI replacing Jira at scale.
MEDIUM relevance: devops SaaS raises Series B+; ITSM startup lands major customer; VC blog on dev-tooling disruption.
LOW (exclude): consumer apps, pre-seed under $5M, hardware, pure HR/finance software.
"""
