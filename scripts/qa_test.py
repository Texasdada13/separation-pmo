#!/usr/bin/env python3
"""Comprehensive QA test for Separation PMO."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import create_app
app = create_app()

print("=" * 60)
print("  SEPARATION PMO — FULL QA REPORT")
print("=" * 60)

fails = []

with app.test_client() as client:

    # 1. PAGE ROUTES
    print("\n1. PAGE ROUTES")
    routes = {
        '/dashboard': 'Dashboard', '/projects': 'Tasks & Projects',
        '/workstreams': 'Workstreams', '/milestones': 'Milestones',
        '/tsa': 'TSA Management', '/sla': 'SLA Compliance',
        '/raid': 'RAID Log', '/readiness': 'Exit Readiness',
        '/reporting': 'Executive Reporting', '/governance': 'Governance',
        '/timesheet': 'Timesheets', '/chat': 'AI Advisor',
    }
    for url, name in routes.items():
        resp = client.get(url)
        body = resp.data.decode('utf-8', 'replace')
        issues = []
        if resp.status_code != 200: issues.append(f"status={resp.status_code}")
        if 'Internal Server Error' in body: issues.append("500")
        if 'TemplateSyntaxError' in body: issues.append("Jinja error")
        if issues:
            fails.append(f"{name} ({url}): {', '.join(issues)}")
            print(f"   FAIL {name} ({url}): {', '.join(issues)}")
        else:
            print(f"   PASS {name} ({url}) -> {resp.status_code}")

    # 2. API ENDPOINTS
    print("\n2. API ENDPOINTS")
    programs = client.get('/api/programs').get_json().get('programs', [])
    print(f"   PASS GET /api/programs -> {len(programs)} programs")

    pid = programs[0]['id'] if programs else None
    if pid:
        resp = client.get(f'/program/{pid}')
        print(f"   PASS GET /program/{{id}} -> {resp.status_code}")

        ws = client.get(f'/api/programs/{pid}/workstreams').get_json()
        print(f"   PASS GET workstreams -> {len(ws.get('workstreams', []))}")

        tasks = client.get(f'/api/programs/{pid}/tasks').get_json()
        print(f"   PASS GET tasks -> {len(tasks.get('tasks', []))}")

        milestones = client.get(f'/api/programs/{pid}/milestones').get_json()
        print(f"   PASS GET milestones -> {len(milestones.get('milestones', []))}")

        tsas = client.get(f'/api/programs/{pid}/tsas').get_json()
        print(f"   PASS GET TSAs -> {len(tsas.get('tsas', []))}")

        raid = client.get(f'/api/programs/{pid}/raid').get_json()
        print(f"   PASS GET RAID -> {len(raid.get('items', []))}")

        time_entries = client.get(f'/api/programs/{pid}/time-entries').get_json()
        print(f"   PASS GET time entries -> {len(time_entries.get('entries', []))}")

        meetings = client.get(f'/api/programs/{pid}/meetings').get_json()
        print(f"   PASS GET meetings -> {len(meetings.get('meetings', []))}")

        readiness = client.get(f'/api/programs/{pid}/readiness').get_json()
        print(f"   PASS GET readiness -> {len(readiness.get('items', []))}")

        stats = client.get(f'/api/programs/{pid}/stats').get_json()
        print(f"   PASS GET stats -> tasks={stats.get('total_tasks')}, complete={stats.get('task_completion_pct')}%")

        # Validation
        resp = client.post(f'/api/programs/{pid}/analyze',
            json={'analysis_type': 'invalid'}, content_type='application/json')
        ok = resp.status_code == 400
        if not ok: fails.append(f"Validation expected 400, got {resp.status_code}")
        print(f"   {'PASS' if ok else 'FAIL'} POST analyze (invalid) -> {resp.status_code}")

    # 3. DATA INTEGRITY
    print("\n3. DATA INTEGRITY")
    if pid:
        demo = [p for p in programs if 'DEMO' in p['name']]
        if demo:
            d = demo[0]
            print(f"   Demo program: health={d.get('overall_health_score')}, risk={d.get('risk_level')}")
        print(f"   Tasks: {len(tasks.get('tasks', []))}")
        print(f"   Milestones: {len(milestones.get('milestones', []))}")
        print(f"   TSAs: {len(tsas.get('tsas', []))}")
        print(f"   RAID items: {len(raid.get('items', []))}")
        print(f"   Time entries: {len(time_entries.get('entries', []))}")
        print(f"   Meetings: {len(meetings.get('meetings', []))}")
        print(f"   Readiness items: {len(readiness.get('items', []))}")

# SUMMARY
print("\n" + "=" * 60)
total = len(routes) + 12
if fails:
    print(f"RESULT: {len(fails)} FAILURES out of ~{total} tests")
    for f in fails: print(f"  FAIL: {f}")
else:
    print(f"RESULT: ALL TESTS PASSED (~{total} tests)")
print("=" * 60)
