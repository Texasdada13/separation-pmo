#!/usr/bin/env python3
"""Exhaustive QA test for Phase 7 features."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import create_app
app = create_app()

fails = []
total = 0

def check(name, condition, detail=''):
    global total
    total += 1
    if condition:
        print(f'   PASS {name}')
    else:
        fails.append(f'{name}: {detail}')
        print(f'   FAIL {name}: {detail}')

print('=' * 60)
print('  EXHAUSTIVE QA — Phase 7 Features')
print('=' * 60)

with app.test_client() as client:
    # Get program
    programs = client.get('/api/programs').get_json()['programs']
    pid = programs[0]['id']

    # ============================================================
    print('\n1. NEW PAGE: /analytics')
    # ============================================================
    resp = client.get('/analytics')
    check('Analytics page loads', resp.status_code == 200)
    check('Has BI heading', b'Business Intelligence' in resp.data)
    check('Has program selector', b'programSelect' in resp.data)
    check('Has Chart.js charts', b'taskStatusChart' in resp.data)
    check('Has scorecard section', b'Executive Scorecard' in resp.data)
    check('Has workstream heatmap', b'wsHeatmapContainer' in resp.data)
    check('Has TSA analytics', b'TSA Analytics' in resp.data)
    check('Has RAID analytics', b'Risk Heat Map' in resp.data)
    check('Has effort analytics', b'Work Effort Analytics' in resp.data)
    check('Has readiness section', b'Readiness by Workstream' in resp.data)
    check('Has export button', b'Export' in resp.data)

    # ============================================================
    print('\n2. ANALYTICS API — DATA VALIDATION')
    # ============================================================
    resp = client.get(f'/api/programs/{pid}/analytics')
    check('Analytics API returns 200', resp.status_code == 200)
    data = resp.get_json()

    expected_keys = ['program', 'scorecard', 'workstream_heatmap', 'task_velocity',
        'task_status', 'task_priority', 'tsa_by_category', 'tsa_exit_timeline',
        'tsa_cost_burndown', 'raid_by_type', 'risk_heatmap', 'raid_by_workstream',
        'raid_aging', 'effort_by_workstream', 'effort_by_person', 'effort_by_category',
        'effort_by_week', 'readiness_by_workstream', 'milestones']
    for key in expected_keys:
        check(f'Analytics has key: {key}', key in data, 'missing from response')

    # Scorecard values
    sc = data.get('scorecard', {})
    check('Scorecard health_score is numeric', isinstance(sc.get('health_score'), (int, float)))
    check('Scorecard task_pct is 0-100', 0 <= sc.get('task_pct', -1) <= 100)
    check('Scorecard milestone_pct is 0-100', 0 <= sc.get('milestone_pct', -1) <= 100)
    check('Scorecard readiness_pct is 0-100', 0 <= sc.get('readiness_pct', -1) <= 100)
    check('Scorecard tsa_exit_pct is 0-100', 0 <= sc.get('tsa_exit_pct', -1) <= 100)
    check('Scorecard open_risks >= 0', sc.get('open_risks', -1) >= 0)
    check('Scorecard open_issues >= 0', sc.get('open_issues', -1) >= 0)
    check('Scorecard total_effort_hours >= 0', sc.get('total_effort_hours', -1) >= 0)

    # Workstream heatmap
    hm = data.get('workstream_heatmap', [])
    check('Workstream heatmap has 9 entries', len(hm) == 9)
    if hm:
        ws0 = hm[0]
        check('Heatmap entry has name', 'name' in ws0)
        check('Heatmap entry has percent_complete', 'percent_complete' in ws0)
        check('Heatmap entry has total_tasks', 'total_tasks' in ws0)
        check('Heatmap entry has completed', 'completed' in ws0)
        check('Heatmap entry has blocked', 'blocked' in ws0)
        check('Heatmap entry has status', 'status' in ws0)
        check('Heatmap entry has lead', 'lead' in ws0)

    # Task velocity
    vel = data.get('task_velocity', [])
    check('Task velocity has 12 weeks', len(vel) == 12)
    if vel:
        check('Velocity entry has week + completed', 'week' in vel[0] and 'completed' in vel[0])
        check('Velocity completed values non-negative', all(v['completed'] >= 0 for v in vel))

    # Task status
    ts = data.get('task_status', {})
    check('Task status has entries', len(ts) > 0)

    # Task priority
    tp = data.get('task_priority', {})
    check('Task priority has entries', len(tp) > 0)

    # TSA timeline
    tsa_tl = data.get('tsa_exit_timeline', [])
    check('TSA timeline has entries', len(tsa_tl) > 0)
    if tsa_tl:
        t0 = tsa_tl[0]
        for field in ['service', 'category', 'exit_date', 'status', 'monthly_cost', 'readiness']:
            check(f'TSA timeline has {field}', field in t0)

    # TSA by category
    tsa_cat = data.get('tsa_by_category', {})
    check('TSA by category has entries', len(tsa_cat) > 0)
    if tsa_cat:
        first = list(tsa_cat.values())[0]
        check('TSA category has count/monthly_cost/active/exited', all(k in first for k in ['count', 'monthly_cost', 'active', 'exited']))

    # TSA cost burndown
    burndown = data.get('tsa_cost_burndown', [])
    check('TSA cost burndown has entries', len(burndown) > 0)
    if burndown:
        check('Burndown has month + cost', 'month' in burndown[0] and 'cost' in burndown[0])
        check('Burndown costs non-negative', all(b['cost'] >= 0 for b in burndown))
        check('Burndown shows decreasing trend', burndown[0]['cost'] >= burndown[-1]['cost'])

    # RAID by type
    raid = data.get('raid_by_type', {})
    check('RAID has risk type', 'risk' in raid)
    check('RAID has action type', 'action' in raid)
    check('RAID has issue type', 'issue' in raid)
    if 'risk' in raid:
        check('RAID risk has open/closed/total', all(k in raid['risk'] for k in ['open', 'closed', 'total']))

    # Risk heatmap
    risk_hm = data.get('risk_heatmap', [])
    check('Risk heatmap has entries', len(risk_hm) > 0)
    if risk_hm:
        r0 = risk_hm[0]
        check('Risk heatmap has title', 'title' in r0)
        check('Risk heatmap has impact (1-5)', 1 <= r0.get('impact', 0) <= 5)
        check('Risk heatmap has likelihood (1-5)', 1 <= r0.get('likelihood', 0) <= 5)
        check('Risk heatmap has score', 'score' in r0)
        check('Risk score = impact * likelihood', r0.get('score') == r0.get('impact', 0) * r0.get('likelihood', 0))

    # RAID aging
    aging = data.get('raid_aging', {})
    check('RAID aging has all 4 buckets', all(k in aging for k in ['0-7', '8-14', '15-30', '30+']))
    check('RAID aging values non-negative', all(v >= 0 for v in aging.values()))

    # RAID by workstream
    raid_ws = data.get('raid_by_workstream', {})
    check('RAID by workstream has entries', len(raid_ws) > 0)

    # Effort by workstream
    eff_ws = data.get('effort_by_workstream', {})
    check('Effort by workstream has entries', len(eff_ws) > 0)
    if eff_ws:
        first = list(eff_ws.values())[0]
        check('Effort ws has internal/client', 'internal' in first and 'client' in first)

    # Effort by person
    eff_person = data.get('effort_by_person', {})
    check('Effort by person has entries', len(eff_person) > 0)
    if eff_person:
        first = list(eff_person.values())[0]
        check('Person effort has hours/billable', 'hours' in first and 'billable' in first)
        check('Person hours > 0', first['hours'] > 0)

    # Effort by week
    eff_week = data.get('effort_by_week', [])
    check('Effort by week has 12 entries', len(eff_week) == 12)
    if eff_week:
        check('Week entry has week/hours', 'week' in eff_week[0] and 'hours' in eff_week[0])

    # Effort by category
    eff_cat = data.get('effort_by_category', {})
    check('Effort by category has entries', len(eff_cat) > 0)

    # Milestones
    ms = data.get('milestones', {})
    check('Milestones has all 4 statuses', all(k in ms for k in ['on_track', 'at_risk', 'complete', 'missed']))

    # Readiness by workstream
    readiness = data.get('readiness_by_workstream', {})
    check('Readiness by ws has entries', len(readiness) > 0)
    if readiness:
        first = list(readiness.values())[0]
        check('Readiness has ready/total/critical_ready/critical_total',
              all(k in first for k in ['ready', 'total', 'critical_ready', 'critical_total']))

    # ============================================================
    print('\n3. ANALYTICS API — EDGE CASES')
    # ============================================================
    resp = client.get('/api/programs/nonexistent-id-12345/analytics')
    check('Analytics 404 for bad program', resp.status_code == 404)

    # ============================================================
    print('\n4. SEED DEMO API')
    # ============================================================
    resp = client.post('/api/seed-demo')
    check('Seed demo returns 200', resp.status_code == 200)
    check('Seed demo returns success', resp.get_json().get('success') == True)

    # ============================================================
    print('\n5. ONBOARDING — DASHBOARD')
    # ============================================================
    resp = client.get('/dashboard')
    body = resp.data
    check('Dashboard has Load Demo button', b'Load Demo Program' in body)
    check('Dashboard has seed-demo API call', b'seed-demo' in body)
    check('Dashboard has loadDemoData function', b'loadDemoData' in body)
    # Note: with demo data loaded, onboarding {% else %} block won't render.
    # Verify the template source contains the onboarding flow.
    with open('web/templates/dashboard.html') as f:
        tpl = f.read()
    check('Dashboard template has 3-step onboarding', 'Create Program' in tpl and 'Build Workplan' in tpl and 'Track' in tpl)

    # ============================================================
    print('\n6. AI BUTTONS — READINESS PAGE')
    # ============================================================
    resp = client.get('/readiness')
    body = resp.data
    check('Readiness page loads', resp.status_code == 200)
    check('Has AI Assess button', b'btnAiReadiness' in body)
    check('Has runAiReadiness function', b'runAiReadiness' in body)
    check('Has aiReadinessCard container', b'aiReadinessCard' in body)
    check('Calls readiness_assessment type', b'readiness_assessment' in body)

    # ============================================================
    print('\n7. AI BUTTONS — RAID PAGE')
    # ============================================================
    resp = client.get('/raid')
    body = resp.data
    check('RAID page loads', resp.status_code == 200)
    check('Has AI Analyze button', b'btnAiRisk' in body)
    check('Has runAiRiskAnalysis function', b'runAiRiskAnalysis' in body)
    check('Has aiRiskCard container', b'aiRiskCard' in body)
    check('Calls risk_analysis type', b'risk_analysis' in body)

    # ============================================================
    print('\n8. TIMESHEET — UTILIZATION + ACTIVITY TABS')
    # ============================================================
    resp = client.get('/timesheet')
    body = resp.data
    check('Timesheet page loads', resp.status_code == 200)
    check('Has Utilization tab', b'Utilization' in body)
    check('Has Activity Log tab', b'Activity Log' in body)
    check('Has utilizationView div', b'utilizationView' in body)
    check('Has activityView div', b'activityView' in body)
    check('Has weeklyTrendChart canvas', b'weeklyTrendChart' in body)
    check('Has activityPieChart canvas', b'activityPieChart' in body)
    check('Has utilizationBody table', b'utilizationBody' in body)
    check('Has activityLogBody container', b'activityLogBody' in body)
    check('Has renderUtilization function', b'renderUtilization' in body)
    check('Has renderActivityLog function', b'renderActivityLog' in body)
    check('Has renderWeeklyTrend function', b'renderWeeklyTrend' in body)
    check('Has renderActivityPie function', b'renderActivityPie' in body)
    check('Has renderUtilizationTable function', b'renderUtilizationTable' in body)
    check('4 view tabs total', body.count(b'switchView(') >= 4)

    # ============================================================
    print('\n9. PROJECTS — CLIENT TASKS TAB')
    # ============================================================
    resp = client.get('/projects')
    body = resp.data
    check('Projects page loads', resp.status_code == 200)
    check('Has Client Tasks tab', b'Client Tasks' in body)
    check('Has clientView div', b'clientView' in body)
    check('Has clientTaskBody table', b'clientTaskBody' in body)
    check('Has renderClientTasks function', b'renderClientTasks' in body)
    check('Has client metric: clientTotal', b'clientTotal' in body)
    check('Has client metric: clientComplete', b'clientComplete' in body)
    check('Has client metric: clientOverdue', b'clientOverdue' in body)
    check('Has client metric: clientPct', b'clientPct' in body)

    # ============================================================
    print('\n10. REPORTING PAGE (verify intact)')
    # ============================================================
    resp = client.get('/reporting')
    body = resp.data
    check('Reporting page loads', resp.status_code == 200)
    check('Has Status Report button', b'btnStatusReport' in body)
    check('Has Risk Report button', b'btnRiskReport' in body)
    check('Has Readiness Report button', b'btnReadinessReport' in body)
    check('Has generateReport function', b'generateReport' in body)
    check('Has Past Reports table', b'pastReportsBody' in body)

    # ============================================================
    print('\n11. AI ANALYSIS API (all 5 types + validation)')
    # ============================================================
    # Re-fetch pid since seed-demo may have recreated the program
    programs = client.get('/api/programs').get_json()['programs']
    pid = programs[0]['id']
    for atype in ['status_report', 'risk_analysis', 'readiness_assessment', 'program_health', 'tsa_risk']:
        resp = client.post(f'/api/programs/{pid}/analyze',
                          json={'analysis_type': atype}, content_type='application/json')
        check(f'AI {atype} returns 200', resp.status_code == 200)
        result = resp.get_json() or {}
        check(f'AI {atype} has results', 'results' in result)
        r = result.get('results', {}) or {}
        check(f'AI {atype} has overall_score', 'overall_score' in r)
        check(f'AI {atype} has grade', 'grade' in r)

    resp = client.post(f'/api/programs/{pid}/analyze',
                      json={'analysis_type': 'bogus_type'}, content_type='application/json')
    check('Invalid analysis type returns 400', resp.status_code == 400)

    resp = client.post(f'/api/programs/{pid}/analyze',
                      json={}, content_type='application/json')
    check('Missing analysis_type returns 400', resp.status_code == 400)

    # ============================================================
    print('\n12. NAVIGATION')
    # ============================================================
    resp = client.get('/dashboard')
    check('Nav has Analytics link', b'/analytics' in resp.data)
    check('Nav has bi-graph-up-arrow icon', b'bi-graph-up-arrow' in resp.data)

    # ============================================================
    print('\n13. DEV TOOLING')
    # ============================================================
    check('start_dev.py exists', os.path.exists('start_dev.py'))
    check('.vscode/tasks.json exists', os.path.exists('.vscode/tasks.json'))

    with open('.vscode/tasks.json') as f:
        tasks_config = json.load(f)
    tasks_list = tasks_config.get('tasks', [])
    check('tasks.json has 3 tasks', len(tasks_list) == 3)
    start_task = tasks_list[0] if tasks_list else {}
    check('First task runs on folderOpen', start_task.get('runOptions', {}).get('runOn') == 'folderOpen')
    check('First task runs start_dev.py', 'start_dev.py' in str(start_task.get('args', [])))

    # ============================================================
    print('\n14. CONFIG FIX')
    # ============================================================
    with open('config/settings.py') as f:
        config_content = f.read()
    check('Config uses absolute path', '_project_root' in config_content)
    check('Config uses os.path.abspath', 'os.path.abspath' in config_content)

    # ============================================================
    print('\n15. ALL 13 PAGES — NO ERRORS')
    # ============================================================
    all_pages = ['/dashboard', '/analytics', '/projects', '/workstreams', '/milestones',
                 '/tsa', '/sla', '/raid', '/readiness', '/reporting', '/governance',
                 '/timesheet', '/chat']
    for page in all_pages:
        resp = client.get(page)
        body = resp.data.decode('utf-8', 'replace')
        check(f'{page} returns 200', resp.status_code == 200)
        check(f'{page} no 500 error', 'Internal Server Error' not in body)
        check(f'{page} no Jinja error', 'TemplateSyntaxError' not in body)

    # ============================================================
    print('\n16. ALL EXISTING API ENDPOINTS')
    # ============================================================
    # Re-fetch pid in case it changed
    programs = client.get('/api/programs').get_json()['programs']
    pid = programs[0]['id']
    api_checks = [
        ('/api/programs', 'GET'),
        (f'/api/programs/{pid}', 'GET'),
        (f'/api/programs/{pid}/workstreams', 'GET'),
        (f'/api/programs/{pid}/tasks', 'GET'),
        (f'/api/programs/{pid}/milestones', 'GET'),
        (f'/api/programs/{pid}/tsas', 'GET'),
        (f'/api/programs/{pid}/raid', 'GET'),
        (f'/api/programs/{pid}/time-entries', 'GET'),
        (f'/api/programs/{pid}/meetings', 'GET'),
        (f'/api/programs/{pid}/readiness', 'GET'),
        (f'/api/programs/{pid}/stats', 'GET'),
        (f'/api/programs/{pid}/analyses', 'GET'),
        (f'/api/programs/{pid}/analytics', 'GET'),
    ]
    for url, method in api_checks:
        resp = client.get(url) if method == 'GET' else client.post(url)
        check(f'{method} {url.replace(pid, "<id>")}', resp.status_code == 200)

# ============================================================
# SUMMARY
# ============================================================
print('\n' + '=' * 60)
if fails:
    print(f'RESULT: {len(fails)} FAILURES out of {total} tests')
    for f in fails:
        print(f'  FAIL: {f}')
else:
    print(f'RESULT: ALL {total} TESTS PASSED')
print('=' * 60)
sys.exit(1 if fails else 0)
