#!/usr/bin/env python3
"""
Seed script for Separation PMO demo data.

Creates a realistic demo separation program with workstreams, tasks,
milestones, TSAs, SLAs, RAID items, time entries, meetings, and
readiness items. Idempotent — safe to run multiple times.

Usage:
    python scripts/seed_demo.py
"""

import sys
import os
from datetime import datetime, date, timedelta
from random import choice, randint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEMO_PROGRAM_NAME = "[DEMO] Acme Corp Divestiture"


def seed(use_existing_context=False):
    from src.database.models import (
        db, Program, Workstream, Task, Milestone, TSAAgreement,
        SLAMetric, RAIDItem, TimeEntry, GovernanceMeeting,
        ReadinessItem
    )

    def _do_seed():
        existing = Program.query.filter_by(name=DEMO_PROGRAM_NAME).first()
        if existing:
            print(f"Demo program exists (id={existing.id}). Deleting and re-seeding...")
            db.session.delete(existing)
            db.session.commit()

        # -----------------------------------------------------------
        # 1. Program
        # -----------------------------------------------------------
        program = Program(
            name=DEMO_PROGRAM_NAME,
            description="12-month carve-out of Acme Corp's Industrial Services division. "
                        "$850M transaction with Global Partners PE as acquirer.",
            program_type="carve-out",
            status="execution",
            buyer_name="Global Partners PE",
            seller_name="Acme Corporation",
            deal_value=850000000,
            start_date=date(2025, 10, 1),
            day1_date=date(2026, 4, 1),
            target_end_date=date(2026, 9, 30),
            overall_health_score=72.0,
            risk_level="Medium",
            program_lead="Sarah Chen",
            program_lead_email="sarah.chen@tedinitiatives.com",
        )
        db.session.add(program)
        db.session.flush()
        pid = program.id
        print(f"Created program: {program.name} (id={pid})")

        # -----------------------------------------------------------
        # 2. Workstreams
        # -----------------------------------------------------------
        ws_data = [
            ("Finance", "Michael Torres", 65, "on_track"),
            ("Human Resources", "Lisa Wang", 55, "at_risk"),
            ("Information Technology", "James Mitchell", 40, "behind"),
            ("Legal", "Amanda Foster", 70, "on_track"),
            ("Operations", "David Kim", 50, "on_track"),
            ("Procurement", "Rachel Adams", 45, "on_track"),
            ("Supply Chain", "Kevin O'Brien", 35, "at_risk"),
            ("Commercial", "Priya Sharma", 60, "on_track"),
            ("Communications", "Mark Johnson", 75, "on_track"),
        ]
        workstreams = {}
        for i, (name, lead, pct, status) in enumerate(ws_data):
            ws = Workstream(
                program_id=pid, name=name, lead_name=lead,
                percent_complete=pct, status=status, sort_order=i,
                start_date=date(2025, 10, 1), target_end_date=date(2026, 9, 30),
            )
            db.session.add(ws)
            db.session.flush()
            workstreams[name] = ws.id
        print(f"Created 9 workstreams")

        # -----------------------------------------------------------
        # 3. Tasks (~60 tasks across workstreams)
        # -----------------------------------------------------------
        task_templates = {
            "Finance": [
                ("Standalone financial statements preparation", "critical", "complete", 40),
                ("Chart of accounts design", "high", "complete", 24),
                ("Banking relationship setup", "high", "in_progress", 16),
                ("Tax entity structuring", "critical", "in_progress", 32),
                ("Intercompany transaction elimination", "high", "in_progress", 20),
                ("Standalone audit preparation", "medium", "not_started", 40),
                ("Financial reporting package design", "medium", "not_started", 16),
            ],
            "Human Resources": [
                ("Employee census and allocation", "critical", "complete", 20),
                ("Benefits plan design", "critical", "in_progress", 40),
                ("Payroll system setup", "high", "in_progress", 32),
                ("Employee communications plan", "high", "in_progress", 16),
                ("HRIS data migration", "critical", "blocked", 48),
                ("Compensation benchmarking", "medium", "not_started", 24),
                ("Offer letter generation", "high", "not_started", 16),
            ],
            "Information Technology": [
                ("Application portfolio assessment", "critical", "complete", 40),
                ("Network separation design", "critical", "in_progress", 60),
                ("Data migration planning", "critical", "in_progress", 48),
                ("ERP configuration (standalone)", "critical", "blocked", 80),
                ("Email and collaboration migration", "high", "not_started", 32),
                ("Cybersecurity assessment", "high", "in_progress", 24),
                ("Infrastructure provisioning", "critical", "not_started", 60),
                ("User acceptance testing", "high", "not_started", 40),
            ],
            "Legal": [
                ("TSA master agreement drafting", "critical", "complete", 60),
                ("IP assignment and licensing", "critical", "complete", 40),
                ("Contract novation/assignment", "high", "in_progress", 48),
                ("Regulatory filings", "critical", "in_progress", 24),
                ("Employee transfer agreements", "high", "in_progress", 20),
                ("Real estate lease assignments", "medium", "not_started", 32),
                ("Insurance policy transfers", "medium", "not_started", 16),
            ],
            "Operations": [
                ("Facility assessment and allocation", "high", "complete", 32),
                ("Manufacturing line separation", "critical", "in_progress", 60),
                ("Quality system standalone setup", "high", "in_progress", 40),
                ("Safety and compliance transfer", "high", "not_started", 24),
                ("Equipment and asset tagging", "medium", "in_progress", 20),
                ("Operational procedures documentation", "medium", "not_started", 32),
            ],
            "Procurement": [
                ("Vendor contract review", "high", "complete", 24),
                ("Supplier notification and novation", "critical", "in_progress", 40),
                ("Purchasing system setup", "high", "not_started", 32),
                ("Spend analytics and categorization", "medium", "in_progress", 16),
                ("Strategic sourcing for standalone", "medium", "not_started", 24),
            ],
            "Supply Chain": [
                ("Distribution network assessment", "critical", "in_progress", 32),
                ("Warehouse management system setup", "critical", "blocked", 48),
                ("Logistics provider negotiations", "high", "in_progress", 24),
                ("Inventory transfer planning", "high", "not_started", 20),
                ("Demand planning system setup", "medium", "not_started", 32),
            ],
            "Commercial": [
                ("Customer communication plan", "critical", "complete", 16),
                ("CRM data migration", "high", "in_progress", 32),
                ("Sales team transition", "high", "in_progress", 24),
                ("Pricing strategy review", "medium", "in_progress", 20),
                ("Go-to-market standalone plan", "high", "not_started", 40),
                ("Channel partner notifications", "medium", "not_started", 16),
            ],
            "Communications": [
                ("Internal comms plan", "critical", "complete", 16),
                ("External stakeholder messaging", "high", "complete", 12),
                ("Brand transition plan", "high", "in_progress", 24),
                ("Town hall presentations", "medium", "complete", 8),
                ("Day 1 communications package", "critical", "in_progress", 20),
            ],
        }

        base_date = date(2025, 10, 15)
        task_count = 0
        for ws_name, tasks in task_templates.items():
            ws_id = workstreams[ws_name]
            for j, (title, priority, status, est_hours) in enumerate(tasks):
                start = base_date + timedelta(days=j * 14 + randint(0, 7))
                due = start + timedelta(days=randint(14, 45))
                completed = due - timedelta(days=randint(1, 5)) if status == 'complete' else None
                task = Task(
                    program_id=pid, workstream_id=ws_id,
                    title=title, priority=priority, status=status,
                    assignee_name=choice(["Sarah C.", "Mike T.", "Lisa W.", "James M.", "Amanda F.", "David K.", "Rachel A.", "Kevin O.", "Priya S.", "Mark J."]),
                    assignee_type=choice(["internal", "internal", "internal", "client"]),
                    start_date=start, due_date=due, completed_date=completed,
                    estimated_hours=est_hours,
                    actual_hours=est_hours * 0.8 if status == 'complete' else est_hours * 0.4 if status == 'in_progress' else 0,
                    sort_order=j,
                )
                db.session.add(task)
                task_count += 1
        print(f"Created {task_count} tasks")

        # -----------------------------------------------------------
        # 4. Milestones
        # -----------------------------------------------------------
        milestones_data = [
            ("Program Mobilization Complete", "program", date(2025, 11, 1), "complete", True),
            ("TSA Master Agreement Signed", "tsa", date(2025, 12, 15), "complete", True),
            ("Standalone Financial Statements Ready", "workstream", date(2026, 2, 1), "on_track", True),
            ("Day 1 Readiness Assessment", "program", date(2026, 3, 1), "upcoming", True),
            ("Day 1 — Legal Close", "program", date(2026, 4, 1), "upcoming", True),
            ("IT Network Separation Complete", "workstream", date(2026, 5, 15), "at_risk", True),
            ("ERP Go-Live (Standalone)", "workstream", date(2026, 6, 1), "at_risk", True),
            ("HR Systems Migration Complete", "workstream", date(2026, 6, 15), "upcoming", False),
            ("TSA Exit — IT Infrastructure", "tsa", date(2026, 7, 1), "upcoming", True),
            ("TSA Exit — Finance & Accounting", "tsa", date(2026, 8, 1), "upcoming", False),
            ("TSA Exit — HR Services", "tsa", date(2026, 8, 15), "upcoming", False),
            ("Program Close-Out", "program", date(2026, 9, 30), "upcoming", True),
        ]
        for title, mtype, target, status, critical in milestones_data:
            actual = target - timedelta(days=randint(0, 3)) if status == 'complete' else None
            ms = Milestone(
                program_id=pid, title=title, milestone_type=mtype,
                target_date=target, actual_date=actual, status=status,
                owner_name=program.program_lead, is_critical_path=critical,
            )
            db.session.add(ms)
        print(f"Created {len(milestones_data)} milestones")

        # -----------------------------------------------------------
        # 5. TSA Agreements
        # -----------------------------------------------------------
        tsa_data = [
            ("IT Infrastructure Services", "IT", "Acme Corp", "NewCo", 125000, date(2026, 4, 1), date(2026, 9, 30), "active", 45),
            ("Finance & Accounting Support", "Finance", "Acme Corp", "NewCo", 85000, date(2026, 4, 1), date(2026, 8, 31), "active", 60),
            ("HR & Payroll Processing", "HR", "Acme Corp", "NewCo", 65000, date(2026, 4, 1), date(2026, 8, 15), "active", 35),
            ("Facilities & Real Estate", "Operations", "Acme Corp", "NewCo", 45000, date(2026, 4, 1), date(2026, 7, 31), "active", 55),
            ("Procurement Systems Access", "Procurement", "Acme Corp", "NewCo", 25000, date(2026, 4, 1), date(2026, 6, 30), "active", 70),
        ]
        tsa_ids = []
        for name, cat, provider, receiver, cost, start, exit_dt, status, readiness in tsa_data:
            tsa = TSAAgreement(
                program_id=pid, service_name=name, category=cat,
                provider=provider, receiver=receiver,
                monthly_cost=cost, total_cost=cost * 6,
                start_date=start, exit_date=exit_dt, status=status,
                exit_readiness_score=readiness,
                owner_name=choice(["Sarah C.", "Mike T.", "James M."]),
            )
            db.session.add(tsa)
            db.session.flush()
            tsa_ids.append(tsa.id)

            # Add 2-3 SLA metrics per TSA
            sla_templates = [
                ("System Uptime", 99.5, "%", 99.2, "meeting"),
                ("Response Time", 4, "hours", 3.5, "meeting"),
                ("Issue Resolution", 24, "hours", 28, "at_risk"),
                ("Data Accuracy", 99.9, "%", 99.8, "meeting"),
                ("Report Delivery", 5, "business days", 6, "breached"),
            ]
            for sla_name, target, unit, current, sla_status in sla_templates[:randint(2, 4)]:
                sla = SLAMetric(
                    tsa_id=tsa.id, metric_name=sla_name,
                    target_value=target, target_unit=unit,
                    current_value=current, status=sla_status,
                    last_measured_date=date.today() - timedelta(days=randint(1, 7)),
                    breach_count=randint(0, 3) if sla_status == 'breached' else 0,
                )
                db.session.add(sla)
        print(f"Created {len(tsa_data)} TSAs with SLA metrics")

        # -----------------------------------------------------------
        # 6. RAID Items
        # -----------------------------------------------------------
        raid_data = [
            ("risk", "ERP go-live delay impacts Day 1", "IT system readiness is behind schedule. ERP configuration is only 30% complete.", "critical", "James M.", 5, 4, workstreams["Information Technology"]),
            ("risk", "Key employee retention during transition", "3 critical finance team members have expressed concerns about the transition.", "high", "Lisa W.", 4, 3, workstreams["Human Resources"]),
            ("risk", "Vendor contract novation delays", "15 of 42 vendor contracts still require novation. Some vendors are slow to respond.", "high", "Rachel A.", 3, 4, workstreams["Procurement"]),
            ("risk", "Data migration quality issues", "Initial data migration tests showed 2.3% error rate. Target is <0.1%.", "critical", "James M.", 5, 3, workstreams["Information Technology"]),
            ("risk", "TSA cost overruns", "IT TSA costs may exceed budget by 15% if exit is delayed.", "medium", "Sarah C.", 3, 3, None),
            ("issue", "HRIS data migration blocked by vendor", "Current HRIS vendor has not provided data export in required format.", "critical", "Lisa W.", None, None, workstreams["Human Resources"]),
            ("issue", "Warehouse management system licensing delay", "WMS vendor requires 8-week lead time for new license provisioning.", "high", "Kevin O.", None, None, workstreams["Supply Chain"]),
            ("issue", "Customer data privacy review incomplete", "Legal review of customer data transfer requirements still pending.", "high", "Amanda F.", None, None, workstreams["Legal"]),
            ("action", "Complete ERP data mapping for finance module", "Map all GL accounts, cost centers, and profit centers to new structure.", "critical", "Mike T.", None, None, workstreams["Finance"]),
            ("action", "Schedule Day 1 readiness reviews with all workstream leads", "Set up individual sessions to assess readiness status.", "high", "Sarah C.", None, None, None),
            ("action", "Negotiate extended timeline with HRIS vendor", "Escalate data export issue and negotiate resolution timeline.", "critical", "Lisa W.", None, None, workstreams["Human Resources"]),
            ("action", "Develop network separation test plan", "Create comprehensive test plan for network cutover.", "high", "James M.", None, None, workstreams["Information Technology"]),
            ("decision", "Approve standalone ERP platform selection", "SAP S/4HANA vs Oracle Cloud — recommendation presented to SteerCo.", "critical", "Sarah C.", None, None, workstreams["Information Technology"]),
            ("decision", "Confirm Day 1 date of April 1, 2026", "SteerCo to confirm or adjust based on readiness assessment.", "critical", "Sarah C.", None, None, None),
            ("decision", "TSA extension request for IT Infrastructure", "Request 3-month extension from Sept to Dec 2026.", "high", "James M.", None, None, None),
        ]
        for item_type, title, desc, priority, owner, impact, likelihood, ws_id in raid_data:
            item = RAIDItem(
                program_id=pid, workstream_id=ws_id,
                item_type=item_type, title=title, description=desc,
                priority=priority, owner_name=owner,
                raised_by=choice(["Sarah C.", "Mike T.", "Lisa W."]),
                raised_date=date.today() - timedelta(days=randint(5, 60)),
                due_date=date.today() + timedelta(days=randint(7, 45)) if item_type in ('action', 'decision') else None,
                impact_score=impact, likelihood_score=likelihood,
            )
            item.calculate_risk_score()
            db.session.add(item)
        print(f"Created {len(raid_data)} RAID items")

        # -----------------------------------------------------------
        # 7. Time Entries (last 4 weeks)
        # -----------------------------------------------------------
        people = [
            ("Sarah Chen", "internal"), ("Michael Torres", "internal"),
            ("Lisa Wang", "internal"), ("James Mitchell", "internal"),
            ("Amanda Foster", "internal"), ("John Davis", "client"),
            ("Emily Rodriguez", "client"), ("Robert Kim", "client"),
        ]
        categories = ["planning", "execution", "reporting", "meeting", "review", "admin"]
        entry_count = 0
        for week in range(4):
            for person_name, person_type in people:
                for day_offset in range(5):  # Mon-Fri
                    d = date.today() - timedelta(weeks=week, days=day_offset)
                    if d.weekday() >= 5:
                        continue
                    hours = choice([4, 6, 7, 8, 8, 8, 9])
                    entry = TimeEntry(
                        program_id=pid,
                        workstream_id=choice(list(workstreams.values())),
                        person_name=person_name, person_type=person_type,
                        entry_date=d, hours=hours,
                        activity_category=choice(categories),
                        description=f"Work on {choice(['analysis', 'planning', 'migration', 'testing', 'documentation', 'stakeholder meeting', 'design review'])}",
                        billable=person_type == "internal",
                        status="approved" if week > 0 else "submitted",
                    )
                    db.session.add(entry)
                    entry_count += 1
        print(f"Created {entry_count} time entries")

        # -----------------------------------------------------------
        # 8. Governance Meetings
        # -----------------------------------------------------------
        meeting_data = [
            ("Steering Committee", "steering_committee", 90),
            ("Workstream Leads Sync", "workstream_sync", 60),
            ("TSA Review", "tsa_review", 60),
            ("Risk Review", "risk_review", 45),
        ]
        meeting_count = 0
        for title, mtype, duration in meeting_data:
            for week in range(8):
                meeting = GovernanceMeeting(
                    program_id=pid, meeting_type=mtype, title=f"{title} — Week {8-week}",
                    meeting_date=datetime.now() - timedelta(weeks=week, hours=randint(8, 16)),
                    duration_minutes=duration,
                    attendees=["Sarah Chen", "Michael Torres", "Lisa Wang", "James Mitchell"],
                    status="completed" if week > 0 else "scheduled",
                )
                db.session.add(meeting)
                meeting_count += 1
        print(f"Created {meeting_count} governance meetings")

        # -----------------------------------------------------------
        # 9. Readiness Items
        # -----------------------------------------------------------
        readiness_templates = {
            "Finance": [
                ("Standalone chart of accounts configured", "day1", "ready"),
                ("Banking relationships established", "day1", "in_progress"),
                ("Financial reporting templates ready", "day1", "not_started"),
                ("Tax registrations complete", "exit", "in_progress"),
            ],
            "Human Resources": [
                ("Employee offers issued", "day1", "in_progress"),
                ("Benefits enrollment system ready", "day1", "not_started"),
                ("Payroll processing tested", "day1", "blocked"),
                ("HRIS fully migrated", "exit", "not_started"),
            ],
            "Information Technology": [
                ("Network connectivity established", "day1", "in_progress"),
                ("Email migration complete", "day1", "not_started"),
                ("ERP go-live ready", "day1", "not_started"),
                ("All applications migrated", "exit", "not_started"),
                ("Cybersecurity controls in place", "day1", "in_progress"),
            ],
            "Legal": [
                ("All critical contracts novated", "day1", "in_progress"),
                ("Regulatory approvals received", "day1", "ready"),
                ("IP licenses executed", "day1", "ready"),
            ],
            "Operations": [
                ("Facility separation plan executed", "day1", "in_progress"),
                ("Quality systems standalone", "day1", "not_started"),
                ("Safety certifications transferred", "exit", "not_started"),
            ],
        }
        ri_count = 0
        for ws_name, items in readiness_templates.items():
            ws_id = workstreams.get(ws_name)
            for desc, category, status in items:
                ri = ReadinessItem(
                    program_id=pid, workstream_id=ws_id,
                    category=category, item_description=desc,
                    status=status, owner_name=choice(["Sarah C.", "Mike T.", "Lisa W.", "James M."]),
                    target_date=date(2026, 4, 1) if category == "day1" else date(2026, 9, 30),
                    is_critical=status == "blocked" or category == "day1",
                )
                db.session.add(ri)
                ri_count += 1
        print(f"Created {ri_count} readiness items")

        # -----------------------------------------------------------
        # Commit
        # -----------------------------------------------------------
        db.session.commit()
        print(f"\nDemo data seeded successfully!")
        print(f"  Program ID: {pid}")
        print(f"  Dashboard:  http://127.0.0.1:5102/dashboard")
        print(f"  Program:    http://127.0.0.1:5102/program/{pid}")

    import scripts.seed_demo as _self
    _self._seeding = True
    try:
        if use_existing_context:
            # Called from within create_app() — already have an app context
            _do_seed()
        else:
            # Called standalone or from start_dev.py — need our own app context
            from web.app import create_app
            app = create_app()
            with app.app_context():
                _do_seed()
    finally:
        _self._seeding = False


if __name__ == "__main__":
    seed()
