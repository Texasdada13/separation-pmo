"""
Separation PMO — Flask Application

AI-powered Separation Management Office platform for managing
carve-outs, divestitures, and complex transformation programs.
"""

import os
import sys
import logging
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='templates')

    # Load config
    env = os.environ.get('FLASK_ENV', 'development')
    from config.settings import config
    app.config.from_object(config.get(env, config['default']))

    # Extensions
    CORS(app)
    limiter = Limiter(get_remote_address, app=app, default_limits=["100 per minute"])

    # Database
    from src.database.models import (
        db, Program, Workstream, Task, Milestone,
        TSAAgreement, SLAMetric, RAIDItem, TimeEntry,
        GovernanceMeeting, ReadinessItem, Analysis
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")

    # Register patriot-ui-kit
    try:
        from patriot_ui import init_ui
        from patriot_ui.config import NavItem, NavSection
        init_ui(app,
            product_name="Separation PMO",
            product_icon="bi-diagram-3",
            show_org_selector=False,
            nav_sections=[
                NavSection("COMMAND CENTER", [
                    NavItem("Dashboard", "bi-speedometer2", "/dashboard"),
                    NavItem("AI Advisor", "bi-robot", "/chat"),
                ]),
                NavSection("PROJECT MANAGEMENT", [
                    NavItem("Tasks & Projects", "bi-kanban", "/projects"),
                    NavItem("Workstreams", "bi-diagram-3", "/workstreams"),
                    NavItem("Milestones", "bi-flag", "/milestones"),
                ]),
                NavSection("SEPARATION", [
                    NavItem("TSA Management", "bi-file-earmark-text", "/tsa"),
                    NavItem("SLA Compliance", "bi-check2-square", "/sla"),
                    NavItem("RAID Log", "bi-exclamation-diamond", "/raid"),
                    NavItem("Exit Readiness", "bi-door-open", "/readiness"),
                ]),
                NavSection("GOVERNANCE", [
                    NavItem("Executive Reports", "bi-file-earmark-bar-graph", "/reporting"),
                    NavItem("Governance", "bi-building-gear", "/governance"),
                ]),
                NavSection("TRACKING", [
                    NavItem("Timesheets", "bi-clock-history", "/timesheet"),
                ]),
            ]
        )
    except Exception as e:
        logger.warning(f"Could not load patriot-ui-kit: {e}")

    # =============================================================================
    # Page Routes
    # =============================================================================

    @app.route('/')
    def index():
        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    def dashboard():
        programs = Program.query.order_by(Program.created_at.desc()).all()
        return render_template('dashboard.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/program/<program_id>')
    def program_detail(program_id):
        program = Program.query.get_or_404(program_id)
        workstreams = Workstream.query.filter_by(program_id=program_id)\
                                      .order_by(Workstream.sort_order).all()
        tasks = Task.query.filter_by(program_id=program_id)\
                          .order_by(Task.due_date).all()
        milestones = Milestone.query.filter_by(program_id=program_id)\
                                     .order_by(Milestone.target_date).all()
        raid_open = RAIDItem.query.filter_by(program_id=program_id)\
                                   .filter(RAIDItem.status.in_(['open', 'in_progress'])).count()
        tsa_active = TSAAgreement.query.filter_by(program_id=program_id, status='active').count()
        analyses = Analysis.query.filter_by(program_id=program_id)\
                                  .order_by(Analysis.created_at.desc()).limit(10).all()
        return render_template('program_detail.html',
                             app_name=app.config['APP_NAME'],
                             program=program, workstreams=workstreams,
                             tasks=tasks, milestones=milestones,
                             raid_open=raid_open, tsa_active=tsa_active,
                             analyses=analyses,
                             today=date.today())

    @app.route('/projects')
    def projects():
        programs = Program.query.order_by(Program.name).all()
        return render_template('projects.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/workstreams')
    def workstreams():
        programs = Program.query.order_by(Program.name).all()
        return render_template('workstreams.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/milestones')
    def milestones_page():
        programs = Program.query.order_by(Program.name).all()
        return render_template('milestones.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/tsa')
    def tsa():
        programs = Program.query.order_by(Program.name).all()
        return render_template('tsa.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/sla')
    def sla():
        programs = Program.query.order_by(Program.name).all()
        return render_template('sla.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/raid')
    def raid():
        programs = Program.query.order_by(Program.name).all()
        return render_template('raid.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/readiness')
    def readiness():
        programs = Program.query.order_by(Program.name).all()
        return render_template('readiness.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/reporting')
    def reporting():
        programs = Program.query.order_by(Program.name).all()
        return render_template('reporting.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/governance')
    def governance():
        programs = Program.query.order_by(Program.name).all()
        return render_template('governance.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/timesheet')
    def timesheet():
        programs = Program.query.order_by(Program.name).all()
        return render_template('timesheet.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    @app.route('/chat')
    def chat():
        programs = Program.query.order_by(Program.name).all()
        return render_template('chat.html',
                             app_name=app.config['APP_NAME'],
                             programs=programs)

    # =============================================================================
    # API Routes — Programs
    # =============================================================================

    @app.route('/api/programs', methods=['GET'])
    def api_list_programs():
        programs = Program.query.order_by(Program.created_at.desc()).all()
        return jsonify({'programs': [p.to_dict() for p in programs]})

    @app.route('/api/programs', methods=['POST'])
    def api_create_program():
        data = request.json or {}
        program = Program(
            name=data.get('name', 'New Program'),
            description=data.get('description'),
            program_type=data.get('program_type', 'carve-out'),
            buyer_name=data.get('buyer_name'),
            seller_name=data.get('seller_name'),
            program_lead=data.get('program_lead'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            target_end_date=datetime.strptime(data['target_end_date'], '%Y-%m-%d').date() if data.get('target_end_date') else None,
        )
        db.session.add(program)
        db.session.flush()

        # Auto-create 9 workstreams
        workstream_names = ['Finance', 'Human Resources', 'Information Technology', 'Legal',
                           'Operations', 'Procurement', 'Supply Chain', 'Commercial', 'Communications']
        for i, ws_name in enumerate(workstream_names):
            ws = Workstream(
                program_id=program.id,
                name=ws_name,
                sort_order=i,
                start_date=program.start_date,
                target_end_date=program.target_end_date,
            )
            db.session.add(ws)

        db.session.commit()
        return jsonify({'success': True, 'program': program.to_dict()})

    @app.route('/api/programs/<program_id>', methods=['GET'])
    def api_get_program(program_id):
        program = Program.query.get_or_404(program_id)
        return jsonify(program.to_dict())

    @app.route('/api/programs/<program_id>', methods=['DELETE'])
    def api_delete_program(program_id):
        program = Program.query.get_or_404(program_id)
        db.session.delete(program)
        db.session.commit()
        return jsonify({'success': True})

    # =============================================================================
    # API Routes — Workstreams
    # =============================================================================

    @app.route('/api/programs/<program_id>/workstreams', methods=['GET'])
    def api_list_workstreams(program_id):
        workstreams = Workstream.query.filter_by(program_id=program_id)\
                                      .order_by(Workstream.sort_order).all()
        return jsonify({'workstreams': [w.to_dict() for w in workstreams]})

    @app.route('/api/workstreams/<ws_id>', methods=['PUT'])
    def api_update_workstream(ws_id):
        ws = Workstream.query.get_or_404(ws_id)
        data = request.json or {}
        for field in ['name', 'lead_name', 'lead_email', 'status', 'percent_complete', 'description']:
            if field in data:
                setattr(ws, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'workstream': ws.to_dict()})

    # =============================================================================
    # API Routes — Tasks
    # =============================================================================

    @app.route('/api/programs/<program_id>/tasks', methods=['GET'])
    def api_list_tasks(program_id):
        ws_id = request.args.get('workstream_id')
        status = request.args.get('status')
        assignee_type = request.args.get('assignee_type')
        query = Task.query.filter_by(program_id=program_id)
        if ws_id:
            query = query.filter_by(workstream_id=ws_id)
        if status:
            query = query.filter_by(status=status)
        if assignee_type:
            query = query.filter_by(assignee_type=assignee_type)
        tasks = query.order_by(Task.sort_order, Task.due_date).all()
        return jsonify({'tasks': [t.to_dict() for t in tasks]})

    @app.route('/api/programs/<program_id>/tasks', methods=['POST'])
    def api_create_task(program_id):
        data = request.json or {}
        task = Task(
            program_id=program_id,
            workstream_id=data.get('workstream_id'),
            title=data.get('title', 'New Task'),
            description=data.get('description'),
            status=data.get('status', 'not_started'),
            priority=data.get('priority', 'medium'),
            assignee_name=data.get('assignee_name'),
            assignee_type=data.get('assignee_type', 'internal'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            estimated_hours=data.get('estimated_hours'),
            depends_on=data.get('depends_on'),
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'success': True, 'task': task.to_dict()})

    @app.route('/api/tasks/<task_id>', methods=['PUT'])
    def api_update_task(task_id):
        task = Task.query.get_or_404(task_id)
        data = request.json or {}
        for field in ['title', 'description', 'status', 'priority', 'assignee_name',
                      'assignee_type', 'estimated_hours', 'actual_hours', 'sort_order',
                      'is_critical_path', 'depends_on', 'workstream_id']:
            if field in data:
                setattr(task, field, data[field])
        if data.get('start_date'):
            task.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if data.get('due_date'):
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        if data.get('status') == 'complete' and not task.completed_date:
            task.completed_date = date.today()
        db.session.commit()
        return jsonify({'success': True, 'task': task.to_dict()})

    @app.route('/api/tasks/<task_id>', methods=['DELETE'])
    def api_delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True})

    # =============================================================================
    # API Routes — Milestones
    # =============================================================================

    @app.route('/api/programs/<program_id>/milestones', methods=['GET'])
    def api_list_milestones(program_id):
        milestones = Milestone.query.filter_by(program_id=program_id)\
                                     .order_by(Milestone.target_date).all()
        return jsonify({'milestones': [m.to_dict() for m in milestones]})

    @app.route('/api/programs/<program_id>/milestones', methods=['POST'])
    def api_create_milestone(program_id):
        data = request.json or {}
        ms = Milestone(
            program_id=program_id,
            workstream_id=data.get('workstream_id'),
            title=data.get('title', 'New Milestone'),
            description=data.get('description'),
            milestone_type=data.get('milestone_type', 'program'),
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data.get('target_date') else None,
            owner_name=data.get('owner_name'),
            is_critical_path=data.get('is_critical_path', False),
        )
        db.session.add(ms)
        db.session.commit()
        return jsonify({'success': True, 'milestone': ms.to_dict()})

    # =============================================================================
    # API Routes — TSA
    # =============================================================================

    @app.route('/api/programs/<program_id>/tsas', methods=['GET'])
    def api_list_tsas(program_id):
        tsas = TSAAgreement.query.filter_by(program_id=program_id)\
                                  .order_by(TSAAgreement.exit_date).all()
        return jsonify({'tsas': [t.to_dict() for t in tsas]})

    @app.route('/api/programs/<program_id>/tsas', methods=['POST'])
    def api_create_tsa(program_id):
        data = request.json or {}
        tsa = TSAAgreement(
            program_id=program_id,
            service_name=data.get('service_name', 'New TSA'),
            service_description=data.get('service_description'),
            provider=data.get('provider'),
            receiver=data.get('receiver'),
            category=data.get('category'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            exit_date=datetime.strptime(data['exit_date'], '%Y-%m-%d').date() if data.get('exit_date') else None,
            monthly_cost=data.get('monthly_cost'),
            owner_name=data.get('owner_name'),
        )
        db.session.add(tsa)
        db.session.commit()
        return jsonify({'success': True, 'tsa': tsa.to_dict()})

    # =============================================================================
    # API Routes — SLA
    # =============================================================================

    @app.route('/api/tsas/<tsa_id>/slas', methods=['GET'])
    def api_list_slas(tsa_id):
        slas = SLAMetric.query.filter_by(tsa_id=tsa_id).all()
        return jsonify({'slas': [s.to_dict() for s in slas]})

    @app.route('/api/tsas/<tsa_id>/slas', methods=['POST'])
    def api_create_sla(tsa_id):
        data = request.json or {}
        sla = SLAMetric(
            tsa_id=tsa_id,
            metric_name=data.get('metric_name', 'New SLA'),
            description=data.get('description'),
            target_value=data.get('target_value'),
            target_unit=data.get('target_unit'),
            current_value=data.get('current_value'),
            measurement_frequency=data.get('measurement_frequency', 'monthly'),
        )
        db.session.add(sla)
        db.session.commit()
        return jsonify({'success': True, 'sla': sla.to_dict()})

    # =============================================================================
    # API Routes — RAID
    # =============================================================================

    @app.route('/api/programs/<program_id>/raid', methods=['GET'])
    def api_list_raid(program_id):
        item_type = request.args.get('type')
        query = RAIDItem.query.filter_by(program_id=program_id)
        if item_type:
            query = query.filter_by(item_type=item_type)
        items = query.order_by(RAIDItem.created_at.desc()).all()
        return jsonify({'items': [i.to_dict() for i in items]})

    @app.route('/api/programs/<program_id>/raid', methods=['POST'])
    def api_create_raid(program_id):
        data = request.json or {}
        item = RAIDItem(
            program_id=program_id,
            workstream_id=data.get('workstream_id'),
            item_type=data.get('item_type', 'risk'),
            title=data.get('title', 'New Item'),
            description=data.get('description'),
            priority=data.get('priority', 'medium'),
            owner_name=data.get('owner_name'),
            raised_by=data.get('raised_by'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            impact_score=data.get('impact_score'),
            likelihood_score=data.get('likelihood_score'),
            mitigation_plan=data.get('mitigation_plan'),
        )
        item.calculate_risk_score()
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})

    @app.route('/api/raid/<item_id>', methods=['PUT'])
    def api_update_raid(item_id):
        item = RAIDItem.query.get_or_404(item_id)
        data = request.json or {}
        for field in ['title', 'description', 'status', 'priority', 'owner_name',
                      'impact_score', 'likelihood_score', 'mitigation_plan', 'resolution']:
            if field in data:
                setattr(item, field, data[field])
        if data.get('status') == 'closed' and not item.closed_date:
            item.closed_date = date.today()
        item.calculate_risk_score()
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})

    # =============================================================================
    # API Routes — Time Entries
    # =============================================================================

    @app.route('/api/programs/<program_id>/time-entries', methods=['GET'])
    def api_list_time_entries(program_id):
        person_type = request.args.get('person_type')
        query = TimeEntry.query.filter_by(program_id=program_id)
        if person_type:
            query = query.filter_by(person_type=person_type)
        entries = query.order_by(TimeEntry.entry_date.desc()).all()
        return jsonify({'entries': [e.to_dict() for e in entries]})

    @app.route('/api/programs/<program_id>/time-entries', methods=['POST'])
    def api_create_time_entry(program_id):
        data = request.json or {}
        entry = TimeEntry(
            program_id=program_id,
            task_id=data.get('task_id'),
            workstream_id=data.get('workstream_id'),
            person_name=data.get('person_name', 'Unknown'),
            person_type=data.get('person_type', 'internal'),
            entry_date=datetime.strptime(data['entry_date'], '%Y-%m-%d').date() if data.get('entry_date') else date.today(),
            hours=data.get('hours', 0),
            activity_category=data.get('activity_category'),
            description=data.get('description'),
            billable=data.get('billable', True),
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({'success': True, 'entry': entry.to_dict()})

    # =============================================================================
    # API Routes — Governance Meetings
    # =============================================================================

    @app.route('/api/programs/<program_id>/meetings', methods=['GET'])
    def api_list_meetings(program_id):
        meetings = GovernanceMeeting.query.filter_by(program_id=program_id)\
                                          .order_by(GovernanceMeeting.meeting_date.desc()).all()
        return jsonify({'meetings': [m.to_dict() for m in meetings]})

    @app.route('/api/programs/<program_id>/meetings', methods=['POST'])
    def api_create_meeting(program_id):
        data = request.json or {}
        meeting = GovernanceMeeting(
            program_id=program_id,
            meeting_type=data.get('meeting_type', 'workstream_sync'),
            title=data.get('title', 'New Meeting'),
            meeting_date=datetime.strptime(data['meeting_date'], '%Y-%m-%dT%H:%M') if data.get('meeting_date') else datetime.utcnow(),
            duration_minutes=data.get('duration_minutes', 60),
            attendees=data.get('attendees'),
            agenda=data.get('agenda'),
        )
        db.session.add(meeting)
        db.session.commit()
        return jsonify({'success': True, 'meeting': meeting.to_dict()})

    # =============================================================================
    # API Routes — Readiness
    # =============================================================================

    @app.route('/api/programs/<program_id>/readiness', methods=['GET'])
    def api_list_readiness(program_id):
        category = request.args.get('category')
        query = ReadinessItem.query.filter_by(program_id=program_id)
        if category:
            query = query.filter_by(category=category)
        items = query.order_by(ReadinessItem.workstream_id, ReadinessItem.created_at).all()
        return jsonify({'items': [i.to_dict() for i in items]})

    @app.route('/api/programs/<program_id>/readiness', methods=['POST'])
    def api_create_readiness(program_id):
        data = request.json or {}
        item = ReadinessItem(
            program_id=program_id,
            workstream_id=data.get('workstream_id'),
            category=data.get('category', 'day1'),
            item_description=data.get('item_description', 'New Item'),
            owner_name=data.get('owner_name'),
            target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data.get('target_date') else None,
            is_critical=data.get('is_critical', False),
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})

    @app.route('/api/readiness/<item_id>', methods=['PUT'])
    def api_update_readiness(item_id):
        item = ReadinessItem.query.get_or_404(item_id)
        data = request.json or {}
        for field in ['status', 'owner_name', 'evidence_notes']:
            if field in data:
                setattr(item, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'item': item.to_dict()})

    # =============================================================================
    # API Routes — AI Analysis
    # =============================================================================

    @app.route('/api/programs/<program_id>/analyze', methods=['POST'])
    def api_run_analysis(program_id):
        """Run AI-powered analysis for any module type."""
        from src.ai_analysis_engine import get_analysis_engine, AIAnalysisEngine

        program = Program.query.get_or_404(program_id)
        data = request.json or {}
        analysis_type = data.get('analysis_type')
        user_inputs = data.get('inputs', {})

        if not analysis_type:
            return jsonify({'error': 'analysis_type is required'}), 400

        if analysis_type not in AIAnalysisEngine.VALID_TYPES:
            return jsonify({'error': f'Invalid type. Valid: {AIAnalysisEngine.VALID_TYPES}'}), 400

        # Build program context
        workstreams = Workstream.query.filter_by(program_id=program_id).all()
        tasks = Task.query.filter_by(program_id=program_id).all()
        tsas = TSAAgreement.query.filter_by(program_id=program_id).all()
        raid = RAIDItem.query.filter_by(program_id=program_id)\
                              .filter(RAIDItem.status.in_(['open', 'in_progress'])).all()

        context = AIAnalysisEngine.build_program_context(program, workstreams, tasks, tsas, raid)

        engine = get_analysis_engine()
        results = engine.analyze(analysis_type, context, user_inputs)

        if 'error' in results and '_meta' not in results:
            return jsonify(results), 500

        analysis = Analysis(
            program_id=program_id,
            analysis_type=analysis_type,
            overall_score=results.get('overall_score'),
            grade=results.get('grade'),
            inputs=user_inputs,
            results=results,
            model_used=results.get('_meta', {}).get('model'),
        )
        db.session.add(analysis)
        db.session.commit()

        return jsonify({'success': True, 'analysis_id': analysis.id, 'results': results})

    @app.route('/api/programs/<program_id>/analyses', methods=['GET'])
    def api_list_analyses(program_id):
        analysis_type = request.args.get('type')
        query = Analysis.query.filter_by(program_id=program_id)
        if analysis_type:
            query = query.filter_by(analysis_type=analysis_type)
        analyses = query.order_by(Analysis.created_at.desc()).limit(20).all()
        return jsonify({'analyses': [a.to_dict() for a in analyses]})

    @app.route('/api/analyses/<analysis_id>', methods=['GET'])
    def api_get_analysis(analysis_id):
        analysis = Analysis.query.get_or_404(analysis_id)
        return jsonify(analysis.to_dict())

    # =============================================================================
    # API Routes — Program Stats (for dashboard)
    # =============================================================================

    @app.route('/api/programs/<program_id>/stats', methods=['GET'])
    def api_program_stats(program_id):
        total_tasks = Task.query.filter_by(program_id=program_id).count()
        completed_tasks = Task.query.filter_by(program_id=program_id, status='complete').count()
        blocked_tasks = Task.query.filter_by(program_id=program_id, status='blocked').count()
        open_risks = RAIDItem.query.filter_by(program_id=program_id, item_type='risk')\
                                    .filter(RAIDItem.status.in_(['open', 'in_progress'])).count()
        open_issues = RAIDItem.query.filter_by(program_id=program_id, item_type='issue')\
                                     .filter(RAIDItem.status.in_(['open', 'in_progress'])).count()
        overdue_actions = RAIDItem.query.filter_by(program_id=program_id, item_type='action')\
                                        .filter(RAIDItem.status.in_(['open', 'in_progress']))\
                                        .filter(RAIDItem.due_date < date.today()).count()
        active_tsas = TSAAgreement.query.filter_by(program_id=program_id, status='active').count()
        exited_tsas = TSAAgreement.query.filter_by(program_id=program_id, status='exited').count()
        total_milestones = Milestone.query.filter_by(program_id=program_id).count()
        completed_milestones = Milestone.query.filter_by(program_id=program_id, status='complete').count()

        return jsonify({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'task_completion_pct': round(completed_tasks / total_tasks * 100) if total_tasks else 0,
            'blocked_tasks': blocked_tasks,
            'open_risks': open_risks,
            'open_issues': open_issues,
            'overdue_actions': overdue_actions,
            'active_tsas': active_tsas,
            'exited_tsas': exited_tsas,
            'total_milestones': total_milestones,
            'completed_milestones': completed_milestones,
            'milestone_completion_pct': round(completed_milestones / total_milestones * 100) if total_milestones else 0,
        })

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5102))
    app.run(debug=True, port=port, host='0.0.0.0')
