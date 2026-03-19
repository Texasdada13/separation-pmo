"""
Database Models for Separation PMO

SQLAlchemy models for programs, workstreams, tasks, milestones,
TSA agreements, SLA metrics, RAID items, time entries, governance,
and readiness tracking.
"""

import uuid
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


def generate_uuid():
    return str(uuid.uuid4())


# =============================================================================
# CORE PROGRAM MODELS
# =============================================================================


class Program(db.Model):
    """Top-level separation/carve-out program."""
    __tablename__ = 'programs'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    program_type = db.Column(db.String(50), default='carve-out')  # carve-out, divestiture, merger, integration
    status = db.Column(db.String(50), default='mobilization')  # mobilization, execution, stabilization, closed

    # Deal info
    buyer_name = db.Column(db.String(200))
    seller_name = db.Column(db.String(200))
    deal_value = db.Column(db.Float)

    # Dates
    start_date = db.Column(db.Date)
    day1_date = db.Column(db.Date)
    target_end_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)

    # Health
    overall_health_score = db.Column(db.Float)
    risk_level = db.Column(db.String(20))

    # Contact
    program_lead = db.Column(db.String(200))
    program_lead_email = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workstreams = db.relationship('Workstream', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    milestones = db.relationship('Milestone', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    tsa_agreements = db.relationship('TSAAgreement', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    raid_items = db.relationship('RAIDItem', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    time_entries = db.relationship('TimeEntry', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    meetings = db.relationship('GovernanceMeeting', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    readiness_items = db.relationship('ReadinessItem', backref='program', lazy='dynamic', cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='program', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'description': self.description,
            'program_type': self.program_type, 'status': self.status,
            'buyer_name': self.buyer_name, 'seller_name': self.seller_name,
            'deal_value': self.deal_value,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'day1_date': self.day1_date.isoformat() if self.day1_date else None,
            'target_end_date': self.target_end_date.isoformat() if self.target_end_date else None,
            'overall_health_score': self.overall_health_score,
            'risk_level': self.risk_level,
            'program_lead': self.program_lead,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Workstream(db.Model):
    """Functional workstream within a program."""
    __tablename__ = 'workstreams'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    lead_name = db.Column(db.String(200))
    lead_email = db.Column(db.String(200))
    status = db.Column(db.String(50), default='on_track')  # on_track, at_risk, behind, complete
    percent_complete = db.Column(db.Float, default=0)
    start_date = db.Column(db.Date)
    target_end_date = db.Column(db.Date)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tasks = db.relationship('Task', backref='workstream', lazy='dynamic')
    milestones = db.relationship('Milestone', backref='workstream', lazy='dynamic')
    raid_items = db.relationship('RAIDItem', backref='workstream', lazy='dynamic')
    readiness_items = db.relationship('ReadinessItem', backref='workstream', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'name': self.name, 'description': self.description,
            'lead_name': self.lead_name, 'status': self.status,
            'percent_complete': self.percent_complete,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_end_date': self.target_end_date.isoformat() if self.target_end_date else None,
            'sort_order': self.sort_order,
        }


# =============================================================================
# TASK / PROJECT MANAGEMENT
# =============================================================================


class Task(db.Model):
    """Individual task within a workstream."""
    __tablename__ = 'tasks'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)
    workstream_id = db.Column(db.String(36), db.ForeignKey('workstreams.id'))
    parent_task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'))

    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, review, complete, blocked, cancelled
    priority = db.Column(db.String(20), default='medium')  # critical, high, medium, low
    task_type = db.Column(db.String(50), default='task')  # task, deliverable, decision, meeting

    # Assignment
    assignee_name = db.Column(db.String(200))
    assignee_type = db.Column(db.String(20), default='internal')  # internal, client
    assignee_email = db.Column(db.String(200))

    # Dates
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)

    # Effort
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float, default=0)

    # Dependencies (JSON array of task IDs)
    depends_on = db.Column(JSON)
    is_critical_path = db.Column(db.Boolean, default=False)

    # Kanban
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]), lazy='dynamic')
    time_entries = db.relationship('TimeEntry', backref='task', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'workstream_id': self.workstream_id, 'parent_task_id': self.parent_task_id,
            'title': self.title, 'description': self.description,
            'status': self.status, 'priority': self.priority, 'task_type': self.task_type,
            'assignee_name': self.assignee_name, 'assignee_type': self.assignee_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'estimated_hours': self.estimated_hours, 'actual_hours': self.actual_hours,
            'depends_on': self.depends_on, 'is_critical_path': self.is_critical_path,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Milestone(db.Model):
    """Program or workstream milestone."""
    __tablename__ = 'milestones'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)
    workstream_id = db.Column(db.String(36), db.ForeignKey('workstreams.id'))

    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    milestone_type = db.Column(db.String(50), default='program')  # program, workstream, tsa, regulatory
    target_date = db.Column(db.Date)
    actual_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='upcoming')  # upcoming, on_track, at_risk, complete, missed
    owner_name = db.Column(db.String(200))
    is_critical_path = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'workstream_id': self.workstream_id,
            'title': self.title, 'description': self.description,
            'milestone_type': self.milestone_type,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'status': self.status, 'owner_name': self.owner_name,
            'is_critical_path': self.is_critical_path,
        }


# =============================================================================
# TSA & SLA MANAGEMENT
# =============================================================================


class TSAAgreement(db.Model):
    """Transition Services Agreement."""
    __tablename__ = 'tsa_agreements'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)

    service_name = db.Column(db.String(300), nullable=False)
    service_description = db.Column(db.Text)
    provider = db.Column(db.String(200))
    receiver = db.Column(db.String(200))
    category = db.Column(db.String(100))  # IT, Finance, HR, Ops, Legal, Facilities

    # Dates
    start_date = db.Column(db.Date)
    exit_date = db.Column(db.Date)
    extended_exit_date = db.Column(db.Date)

    # Cost
    monthly_cost = db.Column(db.Float)
    total_cost = db.Column(db.Float)

    # Status
    status = db.Column(db.String(50), default='active')  # active, exiting, exited, extended
    exit_readiness_score = db.Column(db.Float)

    # Ownership
    owner_name = db.Column(db.String(200))
    owner_email = db.Column(db.String(200))

    # Dependencies
    dependencies = db.Column(JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sla_metrics = db.relationship('SLAMetric', backref='tsa', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'service_name': self.service_name, 'service_description': self.service_description,
            'provider': self.provider, 'receiver': self.receiver, 'category': self.category,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'monthly_cost': self.monthly_cost, 'total_cost': self.total_cost,
            'status': self.status, 'exit_readiness_score': self.exit_readiness_score,
            'owner_name': self.owner_name, 'dependencies': self.dependencies,
        }


class SLAMetric(db.Model):
    """Service Level Agreement metric for a TSA."""
    __tablename__ = 'sla_metrics'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    tsa_id = db.Column(db.String(36), db.ForeignKey('tsa_agreements.id'), nullable=False)

    metric_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float)
    target_unit = db.Column(db.String(50))  # %, hours, uptime, days, count
    current_value = db.Column(db.Float)
    measurement_frequency = db.Column(db.String(50), default='monthly')  # daily, weekly, monthly
    status = db.Column(db.String(50), default='meeting')  # meeting, at_risk, breached
    last_measured_date = db.Column(db.Date)
    breach_count = db.Column(db.Integer, default=0)
    escalation_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'tsa_id': self.tsa_id,
            'metric_name': self.metric_name, 'description': self.description,
            'target_value': self.target_value, 'target_unit': self.target_unit,
            'current_value': self.current_value, 'status': self.status,
            'measurement_frequency': self.measurement_frequency,
            'last_measured_date': self.last_measured_date.isoformat() if self.last_measured_date else None,
            'breach_count': self.breach_count,
        }


# =============================================================================
# RAID LOG
# =============================================================================


class RAIDItem(db.Model):
    """Risk, Action, Issue, or Decision."""
    __tablename__ = 'raid_items'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)
    workstream_id = db.Column(db.String(36), db.ForeignKey('workstreams.id'))

    item_type = db.Column(db.String(20), nullable=False)  # risk, action, issue, decision
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='open')  # open, in_progress, closed, mitigated, escalated
    priority = db.Column(db.String(20), default='medium')  # critical, high, medium, low

    # Ownership
    owner_name = db.Column(db.String(200))
    raised_by = db.Column(db.String(200))
    raised_date = db.Column(db.Date, default=date.today)

    # Dates
    due_date = db.Column(db.Date)
    closed_date = db.Column(db.Date)

    # Risk scoring
    impact_score = db.Column(db.Integer)  # 1-5
    likelihood_score = db.Column(db.Integer)  # 1-5
    risk_score = db.Column(db.Integer)  # impact * likelihood (calculated)
    ai_risk_score = db.Column(db.Float)

    # Resolution
    mitigation_plan = db.Column(db.Text)
    resolution = db.Column(db.Text)

    # Links
    linked_task_id = db.Column(db.String(36))
    linked_tsa_id = db.Column(db.String(36))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_risk_score(self):
        if self.impact_score and self.likelihood_score:
            self.risk_score = self.impact_score * self.likelihood_score

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'workstream_id': self.workstream_id,
            'item_type': self.item_type, 'title': self.title,
            'description': self.description, 'status': self.status,
            'priority': self.priority, 'owner_name': self.owner_name,
            'raised_by': self.raised_by,
            'raised_date': self.raised_date.isoformat() if self.raised_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'impact_score': self.impact_score, 'likelihood_score': self.likelihood_score,
            'risk_score': self.risk_score, 'ai_risk_score': self.ai_risk_score,
            'mitigation_plan': self.mitigation_plan, 'resolution': self.resolution,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# =============================================================================
# WORK TRACKING
# =============================================================================


class TimeEntry(db.Model):
    """Time/effort entry for work tracking."""
    __tablename__ = 'time_entries'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)
    task_id = db.Column(db.String(36), db.ForeignKey('tasks.id'))
    workstream_id = db.Column(db.String(36), db.ForeignKey('workstreams.id'))

    person_name = db.Column(db.String(200), nullable=False)
    person_type = db.Column(db.String(20), default='internal')  # internal, client
    entry_date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    activity_category = db.Column(db.String(100))  # planning, execution, reporting, meeting, review, admin
    description = db.Column(db.Text)
    billable = db.Column(db.Boolean, default=True)

    approved_by = db.Column(db.String(200))
    approved_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='submitted')  # draft, submitted, approved, rejected

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'task_id': self.task_id, 'workstream_id': self.workstream_id,
            'person_name': self.person_name, 'person_type': self.person_type,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'hours': self.hours, 'activity_category': self.activity_category,
            'description': self.description, 'billable': self.billable,
            'status': self.status,
        }


# =============================================================================
# GOVERNANCE
# =============================================================================


class GovernanceMeeting(db.Model):
    """Governance meeting record."""
    __tablename__ = 'governance_meetings'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)

    meeting_type = db.Column(db.String(100))  # steering_committee, workstream_sync, tsa_review, risk_review, daily_standup
    title = db.Column(db.String(300), nullable=False)
    meeting_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer)
    location = db.Column(db.String(200))

    attendees = db.Column(JSON)
    agenda = db.Column(JSON)
    decisions = db.Column(JSON)
    action_items = db.Column(JSON)
    notes = db.Column(db.Text)

    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled
    materials_url = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'meeting_type': self.meeting_type, 'title': self.title,
            'meeting_date': self.meeting_date.isoformat() if self.meeting_date else None,
            'duration_minutes': self.duration_minutes,
            'attendees': self.attendees, 'decisions': self.decisions,
            'action_items': self.action_items, 'status': self.status,
        }


# =============================================================================
# READINESS
# =============================================================================


class ReadinessItem(db.Model):
    """Day 1 or exit readiness checklist item."""
    __tablename__ = 'readiness_items'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)
    workstream_id = db.Column(db.String(36), db.ForeignKey('workstreams.id'))

    category = db.Column(db.String(50), nullable=False)  # day1, exit, operational
    item_description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, ready, blocked
    owner_name = db.Column(db.String(200))
    target_date = db.Column(db.Date)
    evidence_notes = db.Column(db.Text)
    is_critical = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'workstream_id': self.workstream_id,
            'category': self.category, 'item_description': self.item_description,
            'status': self.status, 'owner_name': self.owner_name,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'is_critical': self.is_critical,
        }


# =============================================================================
# AI ANALYSIS
# =============================================================================


class Analysis(db.Model):
    """AI analysis results (reusable across modules)."""
    __tablename__ = 'analyses'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False, index=True)

    overall_score = db.Column(db.Float)
    grade = db.Column(db.String(5))
    inputs = db.Column(JSON)
    results = db.Column(JSON)
    model_used = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'program_id': self.program_id,
            'analysis_type': self.analysis_type,
            'overall_score': self.overall_score, 'grade': self.grade,
            'inputs': self.inputs, 'results': self.results,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
