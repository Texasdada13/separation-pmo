"""
AI Analysis Engine for Separation PMO

Unified engine for AI-powered analysis across all PMO modules:
program health, workstream assessment, TSA risk, readiness scoring,
RAID analysis, and executive reporting.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.ai_core.claude_client import get_claude_client

logger = logging.getLogger(__name__)


ANALYSIS_PROMPTS = {
    "program_health": {
        "system": "You are a senior transformation program director specializing in carve-outs and divestitures. You assess overall program health and identify risks.\n\nYou MUST respond with valid JSON only.",
        "user": """Assess the overall health of this separation program.

PROGRAM DATA:
{context}

Respond with ONLY this JSON:
{{
  "overall_score": <0-100>,
  "grade": "<A/B/C/D/F>",
  "status_summary": "<2-3 sentence executive summary>",
  "workstream_health": [
    {{"name": "<workstream>", "score": <0-100>, "status": "<on_track/at_risk/behind>", "detail": "<1 sentence>"}}
  ],
  "critical_risks": [
    {{"area": "<area>", "detail": "<description>", "mitigation": "<recommended action>"}}
  ],
  "insights": ["<insight 1>", "<insight 2>", "<insight 3>"],
  "recommendations": [
    {{"title": "<title>", "priority": "<high/medium/low>", "detail": "<1-2 sentences>", "impact": "<expected impact>"}}
  ]
}}"""
    },

    "tsa_risk": {
        "system": "You are a TSA management specialist who has managed hundreds of Transition Services Agreements in carve-out transactions. You identify exit risks and recommend actions.\n\nYou MUST respond with valid JSON only.",
        "user": """Assess the TSA portfolio risk for this separation program.

PROGRAM DATA:
{context}

Respond with ONLY this JSON:
{{
  "overall_score": <0-100 TSA health score>,
  "grade": "<A/B/C/D/F>",
  "at_risk_tsas": [
    {{"service": "<name>", "risk_level": "<high/medium/low>", "exit_date": "<date>", "detail": "<why at risk>", "action": "<recommended>"}}
  ],
  "exit_readiness_by_category": {{
    "IT": <0-100>, "Finance": <0-100>, "HR": <0-100>,
    "Operations": <0-100>, "Legal": <0-100>
  }},
  "cost_analysis": {{
    "monthly_burn": <total monthly cost>,
    "projected_savings_on_exit": <savings>,
    "cost_optimization_opportunities": ["<opportunity>"]
  }},
  "insights": ["<insight 1>", "<insight 2>", "<insight 3>"],
  "recommendations": [
    {{"title": "<title>", "priority": "<high/medium/low>", "detail": "<1-2 sentences>", "impact": "<expected impact>"}}
  ]
}}"""
    },

    "readiness_assessment": {
        "system": "You are a Day 1 readiness and separation execution specialist. You assess whether functional workstreams are ready for operational independence.\n\nYou MUST respond with valid JSON only.",
        "user": """Assess separation readiness across all workstreams.

PROGRAM DATA:
{context}

Respond with ONLY this JSON:
{{
  "overall_score": <0-100 readiness score>,
  "grade": "<A/B/C/D/F>",
  "go_no_go": "<go/conditional_go/no_go>",
  "readiness_by_workstream": [
    {{"workstream": "<name>", "score": <0-100>, "status": "<ready/at_risk/not_ready>", "blockers": ["<blocker>"], "detail": "<1 sentence>"}}
  ],
  "critical_blockers": [
    {{"area": "<area>", "blocker": "<description>", "resolution": "<action needed>", "owner": "<suggested owner>"}}
  ],
  "insights": ["<insight 1>", "<insight 2>", "<insight 3>"],
  "recommendations": [
    {{"title": "<title>", "priority": "<high/medium/low>", "detail": "<1-2 sentences>", "impact": "<expected impact>"}}
  ]
}}"""
    },

    "risk_analysis": {
        "system": "You are an enterprise risk management specialist for M&A transactions. You analyze RAID logs and identify patterns, emerging risks, and mitigation strategies.\n\nYou MUST respond with valid JSON only.",
        "user": """Analyze the RAID log for this separation program and identify patterns and emerging risks.

PROGRAM DATA:
{context}

Respond with ONLY this JSON:
{{
  "overall_score": <0-100 risk management score>,
  "grade": "<A/B/C/D/F>",
  "risk_summary": "<2-3 sentence summary>",
  "top_risks": [
    {{"title": "<risk>", "severity": "<critical/high/medium>", "likelihood": "<high/medium/low>", "impact": "<description>", "mitigation": "<recommended action>"}}
  ],
  "patterns_identified": ["<pattern 1>", "<pattern 2>"],
  "overdue_items": <count>,
  "escalation_needed": [
    {{"item": "<title>", "reason": "<why escalate>", "to_whom": "<role>"}}
  ],
  "insights": ["<insight 1>", "<insight 2>", "<insight 3>"],
  "recommendations": [
    {{"title": "<title>", "priority": "<high/medium/low>", "detail": "<1-2 sentences>", "impact": "<expected impact>"}}
  ]
}}"""
    },

    "status_report": {
        "system": "You are an executive communications specialist who drafts steering committee updates for separation programs. Write clear, concise, executive-ready content.\n\nYou MUST respond with valid JSON only.",
        "user": """Generate a weekly status report for the steering committee.

PROGRAM DATA:
{context}

Respond with ONLY this JSON:
{{
  "overall_score": <0-100 program health>,
  "grade": "<A/B/C/D/F>",
  "executive_summary": "<3-4 sentence summary suitable for steering committee>",
  "workstream_status": [
    {{"workstream": "<name>", "status": "<green/yellow/red>", "highlight": "<1 sentence update>", "next_steps": "<key action>"}}
  ],
  "key_accomplishments": ["<accomplishment 1>", "<accomplishment 2>", "<accomplishment 3>"],
  "upcoming_milestones": [
    {{"milestone": "<name>", "date": "<target date>", "status": "<on_track/at_risk>", "owner": "<name>"}}
  ],
  "risks_and_issues": [
    {{"item": "<title>", "type": "<risk/issue>", "severity": "<high/medium/low>", "action": "<next step>"}}
  ],
  "decisions_needed": [
    {{"decision": "<description>", "by_when": "<date>", "stakeholder": "<who decides>"}}
  ],
  "insights": ["<insight>"],
  "recommendations": [
    {{"title": "<title>", "priority": "<high/medium/low>", "detail": "<detail>", "impact": "<impact>"}}
  ]
}}"""
    },
}


class AIAnalysisEngine:
    """Unified AI analysis engine for Separation PMO."""

    VALID_TYPES = list(ANALYSIS_PROMPTS.keys())

    def __init__(self):
        self.client = get_claude_client()

    def analyze(self, analysis_type, program_context, user_inputs):
        if analysis_type not in self.VALID_TYPES:
            return {"error": f"Unknown type: {analysis_type}. Valid: {self.VALID_TYPES}"}

        prompts = ANALYSIS_PROMPTS[analysis_type]
        context_str = json.dumps(program_context, indent=2, default=str)
        inputs_str = json.dumps(user_inputs, indent=2, default=str)

        user_prompt = prompts["user"].format(context=context_str, inputs=inputs_str)

        if not self.client.is_available():
            return self._fallback(analysis_type, program_context)

        try:
            conv_id = f"pmo_{analysis_type}_{datetime.now().timestamp()}"
            conv = self.client.create_conversation(conv_id)
            conv.system_prompt = prompts["system"]
            conv.add_message("user", user_prompt)
            response = self.client._get_response(conv)
            result = self._parse_json(response)
            result["_meta"] = {
                "analysis_type": analysis_type,
                "model": self.client.model,
                "generated_at": datetime.utcnow().isoformat(),
            }
            return result
        except Exception as e:
            logger.error(f"AI analysis error ({analysis_type}): {e}")
            return {"error": str(e), "analysis_type": analysis_type}

    def _parse_json(self, response):
        text = response.strip()
        if text.startswith("```"):
            lines = [l for l in text.split("\n") if not l.strip().startswith("```")]
            text = "\n".join(lines).strip()
        return json.loads(text)

    def _fallback(self, analysis_type, context):
        return {
            "overall_score": 65, "grade": "C+",
            "insights": ["AI analysis requires ANTHROPIC_API_KEY.", "Set the env var and restart."],
            "recommendations": [{"title": "Enable AI", "priority": "high",
                                 "detail": "Configure API key for full analysis.", "impact": "Full functionality"}],
            "_meta": {"analysis_type": analysis_type, "model": "fallback",
                      "generated_at": datetime.utcnow().isoformat()},
        }

    @staticmethod
    def build_program_context(program, workstreams, tasks, tsas, raid_items):
        total_tasks = len(tasks)
        completed = sum(1 for t in tasks if t.status == 'complete')
        blocked = sum(1 for t in tasks if t.status == 'blocked')

        return {
            "program_name": program.name,
            "program_type": program.program_type,
            "status": program.status,
            "buyer": program.buyer_name,
            "seller": program.seller_name,
            "start_date": str(program.start_date),
            "target_end_date": str(program.target_end_date),
            "day1_date": str(program.day1_date),
            "workstreams": [{"name": w.name, "status": w.status,
                            "percent_complete": w.percent_complete,
                            "lead": w.lead_name} for w in workstreams],
            "task_summary": {
                "total": total_tasks, "completed": completed,
                "blocked": blocked,
                "completion_pct": round(completed / total_tasks * 100) if total_tasks else 0,
            },
            "tsas": [{"service": t.service_name, "category": t.category,
                      "status": t.status, "exit_date": str(t.exit_date),
                      "monthly_cost": t.monthly_cost,
                      "exit_readiness": t.exit_readiness_score} for t in tsas],
            "open_raid": [{"type": r.item_type, "title": r.title,
                          "priority": r.priority, "status": r.status,
                          "risk_score": r.risk_score,
                          "owner": r.owner_name} for r in raid_items],
        }


_engine = None

def get_analysis_engine():
    global _engine
    if _engine is None:
        _engine = AIAnalysisEngine()
    return _engine
