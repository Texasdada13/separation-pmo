# Separation PMO — Implementation Plan

> **Goal:** Build the first AI-powered, purpose-built Separation Management Office platform for managing carve-outs, divestitures, and complex transformation programs.

**Last Updated:** 2026-03-18
**Repo:** [Texasdada13/separation-pmo](https://github.com/Texasdada13/separation-pmo)
**Template Reference:** CFO Intelligence (architecture patterns, patriot-ui-kit, AI engine)

---

## Product Vision

Separation PMO is a standalone platform that replaces the spreadsheets, SharePoint sites, and PowerPoint decks that transformation teams cobble together to manage carve-outs. It provides:

- **Hardcore project management** — tasks, Gantt, Kanban, milestones, dependencies, critical path
- **Separation-specific modules** — TSA lifecycle, SLA compliance, RAID, exit readiness
- **AI-powered intelligence** — auto-generated status reports, risk scoring, readiness assessments
- **Work tracking** — timesheets, activity logs, utilization dashboards, client task accountability
- **Executive reporting** — steering committee materials generated from real program data

**Target users:** Separation Management Office leaders, transformation consultants, PE operating partners, fractional PMO executives.

**Primary use case:** 12-month carve-out/divestiture programs with 9+ functional workstreams and TSA management.

---

## Technical Architecture

### Stack
- **Backend:** Flask 3.x + SQLAlchemy (same as CFO Intelligence)
- **Database:** PostgreSQL (prod) / SQLite (dev)
- **UI:** Patriot UI Kit (Bootstrap 5.3, dark/light themes, navy/gold branding)
- **AI:** Anthropic Claude API via AIAnalysisEngine pattern
- **Charts:** Chart.js with PatriotChartTheme
- **Export:** Browser print-to-PDF, python-docx, reportlab

### Project Structure
```
separation-pmo/
├── web/
│   ├── app.py                    # Flask routes and API endpoints
│   └── templates/
│       ├── base.html             # Extends patriot/base.html with bridge CSS/JS
│       ├── dashboard.html        # Program dashboard
│       ├── projects.html         # Task/project management (Gantt + Kanban)
│       ├── workstreams.html      # Functional workstream tracker
│       ├── tsa.html              # TSA management
│       ├── sla.html              # SLA compliance monitoring
│       ├── raid.html             # RAID log
│       ├── reporting.html        # Executive reporting
│       ├── governance.html       # Governance center
│       ├── readiness.html        # Day 1 / Exit readiness
│       ├── timesheet.html        # Work tracking / timesheets
│       └── chat.html             # AI PMO Advisor
├── src/
│   ├── database/
│   │   └── models.py             # All database models
│   ├── ai_core/
│   │   ├── claude_client.py      # Claude API wrapper (from CFO Intelligence)
│   │   └── chat_engine.py        # PMO-specific chat engine
│   ├── ai_analysis_engine.py     # Unified AI engine with PMO prompts
│   └── patterns/
│       ├── scoring.py            # Readiness scoring engine
│       └── risk_engine.py        # AI risk scoring
├── scripts/
│   ├── seed_demo.py              # Demo program with sample data
│   └── qa_test.py                # QA test suite
├── config/
│   └── settings.py               # App configuration
├── requirements.txt
├── render.yaml
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## Database Models

### Core Models

```
Program
├── id, name, description, program_type (carve-out/divestiture/merger)
├── status (mobilization/execution/stabilization/closed)
├── start_date, target_end_date, actual_end_date
├── buyer_name, seller_name, deal_value
├── overall_health_score, risk_level
└── relationships: workstreams, milestones, tsa_agreements, raid_items

Workstream
├── id, program_id, name (Finance/HR/IT/Legal/Ops/Procurement/Supply Chain/Commercial/Comms)
├── lead_name, lead_email, status, percent_complete
├── start_date, target_end_date
└── relationships: tasks, milestones

Task
├── id, workstream_id, program_id
├── title, description, status (not_started/in_progress/complete/blocked/cancelled)
├── priority (critical/high/medium/low)
├── assignee_name, assignee_type (internal/client)
├── start_date, due_date, completed_date
├── estimated_hours, actual_hours
├── parent_task_id (for subtasks)
├── depends_on (JSON array of task IDs)
├── sort_order (for Kanban)
└── relationships: time_entries, dependencies

Milestone
├── id, program_id, workstream_id (optional)
├── title, description, milestone_type (program/workstream/tsa)
├── target_date, actual_date, status (upcoming/at_risk/complete/missed)
├── owner_name
└── is_critical_path

TSAAgreement
├── id, program_id
├── service_name, service_description
├── provider, receiver
├── category (IT/Finance/HR/Ops/Legal/Facilities)
├── start_date, exit_date, extended_exit_date
├── monthly_cost, total_cost
├── status (active/exiting/exited/extended)
├── exit_readiness_score (0-100)
├── owner_name
├── dependencies (JSON)
└── relationships: sla_metrics, exit_checklist_items

SLAMetric
├── id, tsa_id
├── metric_name, description
├── target_value, target_unit (%, hours, uptime, etc.)
├── current_value, measurement_frequency (daily/weekly/monthly)
├── status (meeting/at_risk/breached)
├── last_measured_date
└── breach_count, escalation_count

RAIDItem
├── id, program_id, workstream_id (optional)
├── item_type (risk/action/issue/decision)
├── title, description
├── status (open/in_progress/closed/mitigated/escalated)
├── priority (critical/high/medium/low)
├── owner_name, raised_by, raised_date
├── due_date, closed_date
├── impact_score (1-5), likelihood_score (1-5)
├── risk_score (impact × likelihood, calculated)
├── mitigation_plan, resolution
├── ai_risk_score (from AI analysis)
└── linked_task_id, linked_tsa_id

TimeEntry
├── id, program_id, task_id (optional), workstream_id (optional)
├── person_name, person_type (internal/client)
├── entry_date, hours
├── activity_category (planning/execution/reporting/meeting/review/admin)
├── description
├── billable (boolean)
└── approved_by, approved_date

GovernanceMeeting
├── id, program_id
├── meeting_type (steering_committee/workstream_sync/tsa_review/risk_review)
├── title, date, duration_minutes
├── attendees (JSON), agenda (JSON)
├── decisions (JSON), action_items (JSON)
├── notes, status (scheduled/completed/cancelled)
└── materials_url

ReadinessItem
├── id, program_id, workstream_id
├── category (day1/exit/operational)
├── item_description
├── status (not_started/in_progress/ready/blocked)
├── owner_name, target_date
├── evidence_notes
└── is_critical

Analysis (from AIAnalysisEngine)
├── id, program_id, analysis_type
├── overall_score, grade, inputs, results
├── model_used, created_at
```

---

## Module Specifications

### Module 1: Program Dashboard
**Route:** `/dashboard`
**Purpose:** Single-pane-of-glass view of the entire separation program.

**Components:**
- Program health score gauge (0-100)
- Program timeline with phase indicator (Mobilization → Day 1 → TSA Exit)
- Workstream status cards (9 cards, each with % complete, status, lead)
- Upcoming milestones (next 30 days)
- Open RAID summary (X risks, Y issues, Z overdue actions)
- TSA exit countdown (days until next TSA exits)
- Recent activity feed
- Key metrics: tasks complete %, milestones on track %, TSAs exited %

### Module 2: Project Management
**Route:** `/projects`
**Purpose:** Hardcore task and project management with Gantt + Kanban views.

**Components:**
- **Task list** — filterable by workstream, assignee, status, priority
- **Gantt chart** — timeline view with dependencies, milestones, critical path highlighting
- **Kanban board** — drag-and-drop columns (Not Started → In Progress → Review → Complete)
- **Task detail modal** — full task info, subtasks, time entries, dependencies, comments
- **Bulk actions** — reassign, change status, change priority
- **Add task** — quick-add with workstream, assignee, dates, priority
- **Dependency tracking** — task A blocks task B, visual dependency lines on Gantt
- **Critical path** — auto-calculated, highlighted in red on Gantt
- **Filters/search** — by workstream, assignee, date range, status, priority

### Module 3: Workstream Tracker
**Route:** `/workstreams`
**Purpose:** Track 9 functional workstreams with status and milestones.

**Components:**
- Workstream cards with lead, status, % complete, task counts
- Expandable detail with milestones and key deliverables
- Cross-workstream dependency visualization
- AI workstream health scoring

### Module 4: TSA Management
**Route:** `/tsa`
**Purpose:** Full lifecycle management of Transition Services Agreements.

**Components:**
- TSA inventory table (service, provider, receiver, cost, exit date, status)
- Exit timeline visualization (Gantt-style showing all TSA exit dates)
- Exit readiness scoring per TSA (0-100)
- Cost tracking (monthly burn, total cost, cost by category)
- Dependency map (which TSAs depend on which)
- Exit checklist per TSA
- AI analysis: "Which TSAs are at risk of missing exit dates?"

### Module 5: SLA Compliance
**Route:** `/sla`
**Purpose:** Monitor service levels across all TSAs.

**Components:**
- SLA dashboard with green/yellow/red status indicators
- Target vs actual for each metric
- Breach log with escalation history
- Trend charts (are SLAs improving or degrading?)
- Compliance score by TSA and overall
- Escalation tracker

### Module 6: RAID Log
**Route:** `/raid`
**Purpose:** Centralized risk, action, issue, and decision tracking.

**Components:**
- Tabbed view: Risks | Actions | Issues | Decisions
- Filterable by workstream, owner, priority, status
- Risk heat map (impact × likelihood matrix)
- AI risk scoring (auto-analyze new items)
- Aging analysis (how long have items been open?)
- Quick-add with type, title, owner, priority
- Link to tasks and TSAs

### Module 7: Executive Reporting
**Route:** `/reporting`
**Purpose:** Auto-generate steering committee materials.

**Components:**
- One-click status report generation (AI pulls from all modules)
- Program scorecard (traffic light by workstream)
- Milestone status summary
- RAID summary with top items
- TSA exit progress
- Customizable report templates
- Export to PDF
- Historical reports archive

### Module 8: Governance Center
**Route:** `/governance`
**Purpose:** Meeting cadence, decisions, and accountability.

**Components:**
- Meeting calendar with cadence (weekly workstream syncs, bi-weekly steering committee, monthly board)
- Decision log with date, decision, owner, status
- RACI matrix by workstream
- Escalation path visualization
- Action items from meetings with follow-up tracking
- Meeting minutes archive

### Module 9: Day 1 / Exit Readiness
**Route:** `/readiness`
**Purpose:** Go/no-go assessment for Day 1 and TSA exits.

**Components:**
- Readiness checklist by workstream (Day 1 items + Exit items)
- Overall readiness score (0-100) with gauge
- Category breakdown (IT ready? Finance ready? HR ready?)
- Go/no-go decision matrix
- Cutover plan timeline
- AI readiness assessment

### Module 10: Work Tracking
**Route:** `/timesheet`
**Purpose:** Track effort, activities, and utilization.

**Components:**
- **Detailed view:** Date, person, hours, workstream, activity, description, billable flag
- **Summary view:** Effort by workstream (bar chart), effort by person (table), weekly totals
- **Internal vs Client:** Toggle between internal team effort and client-side task tracking
- **Utilization dashboard:** Hours by person, % utilization, trend
- **Activity log:** What was done, by whom, when
- **Timesheet approval workflow:** Submit → Review → Approve
- **Export:** CSV/Excel for billing

### Module 11: AI PMO Advisor
**Route:** `/chat`
**Purpose:** Claude-powered PMO assistant with program context.

**Capabilities:**
- "What are my top 3 risks this week?"
- "Draft a steering committee update for Friday"
- "Which TSAs are behind on exit readiness?"
- "Summarize IT workstream progress for the last 2 weeks"
- "Score our overall separation readiness"
- Auto-generate weekly status reports from activity data
- Risk prediction based on task completion trends
- Natural language queries against program data

---

## Implementation Phases

### Phase 0: Foundation
*Project setup, database, base templates, seed data.*

| # | Task | Effort |
|---|------|--------|
| 1 | Project scaffolding (Flask app, config, requirements, patriot-ui-kit) | 2h |
| 2 | Database models (all 10 core models) | 3h |
| 3 | Base template with bridge CSS/JS (from CFO Intelligence) | 1h |
| 4 | Demo seed script (sample program with workstreams, tasks, TSAs, RAID) | 3h |
| 5 | API infrastructure (CRUD for all models) | 4h |
| 6 | AI Analysis Engine with PMO prompts | 2h |

### Phase 1: Core Views
*The pages users see first — dashboard, project management, workstreams.*

| # | Task | Effort |
|---|------|--------|
| 7 | Program Dashboard | 4h |
| 8 | Project Management — task list + Kanban board | 6h |
| 9 | Project Management — Gantt chart with dependencies | 6h |
| 10 | Workstream Tracker | 3h |
| 11 | Navigation and sidebar | 1h |

### Phase 2: Separation-Specific Modules
*The modules that make this a separation tool, not a generic PMO.*

| # | Task | Effort |
|---|------|--------|
| 12 | TSA Management | 5h |
| 13 | SLA Compliance | 4h |
| 14 | RAID Log with AI risk scoring | 5h |
| 15 | Day 1 / Exit Readiness | 4h |

### Phase 3: Reporting & Governance
*Executive-facing features.*

| # | Task | Effort |
|---|------|--------|
| 16 | Executive Reporting (AI-generated) | 5h |
| 17 | Governance Center (meetings, decisions, RACI) | 4h |

### Phase 4: Work Tracking
*Timesheets, activity logs, utilization.*

| # | Task | Effort |
|---|------|--------|
| 18 | Timesheet — detailed entry + summary views | 5h |
| 19 | Activity log + utilization dashboard | 4h |
| 20 | Client task tracking (separate view) | 3h |

### Phase 5: AI & Intelligence
*AI-powered features across the platform.*

| # | Task | Effort |
|---|------|--------|
| 21 | AI PMO Advisor chat | 4h |
| 22 | AI auto-generated status reports | 3h |
| 23 | AI risk prediction + readiness scoring | 3h |

### Phase 6: Polish & Production
*UX, export, onboarding, branding.*

| # | Task | Effort |
|---|------|--------|
| 24 | Tooltips + demo banners across all pages | 2h |
| 25 | PDF export for reports and analyses | 2h |
| 26 | Onboarding flow for empty state | 2h |
| 27 | TED Initiatives alternate branding view | 2h |
| 28 | QA test suite | 2h |
| 29 | Deploy to Render | 1h |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Pages with real functionality | 11/11 (100%) |
| AI-powered features | 5+ (chat, risk scoring, status gen, readiness, analysis) |
| Time to first value | < 5 minutes (seed data + dashboard) |
| Data models | 10+ core models |
| Exportable reports | All modules |

---

## Branding

**Primary:** Patriot Tech Systems (navy/gold, patriot-ui-kit)
**Alternate:** TED Initiatives (to be designed in Phase 6, #27)

---

## File Reference

| File | Purpose |
|------|---------|
| `IMPLEMENTATION_PLAN.md` | This document |
| `web/app.py` | Flask routes and API |
| `web/templates/` | All page templates |
| `src/database/models.py` | Database models |
| `src/ai_analysis_engine.py` | AI engine with PMO prompts |
| `src/ai_core/claude_client.py` | Claude API wrapper |
| `scripts/seed_demo.py` | Demo data |
| `scripts/qa_test.py` | QA tests |
