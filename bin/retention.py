#!/usr/bin/python
"""https://www.youtube.com/watch?v=n_yHZ_vKjno
"""
from __future__ import division, print_function

from collections import defaultdict
from gratipay import wireup

db = wireup.db(wireup.env())

transfers = db.all("select timestamp::date as date, tippee, tipper "
                   "from transfers where context='tip' or context='take' "
                   "order by timestamp", back_as=dict)


# Sort users into cohorts.
# ========================

usermap = {}
cohorts = defaultdict(list)

for transfer in transfers:
    date = transfer['date']
    for username in (transfer['tipper'], transfer['tippee']):
        if username not in usermap:
            usermap[username] = [date, date]
            cohorts[date].append(username)
        else:
            usermap[username][1] = date


# Compute a retentions distribution for each cohort.
# ==================================================

cohort_actives = []
for date, users in sorted(cohorts.items()):

    active = defaultdict(int)
    for username in users:
        start, end = usermap[username]
        nweeks = (end - start).days // 7
        for n in range(nweeks, -1, -1):
            active[n] += 1

    max_weeks = max(active.keys())
    tusers = len(users)

    cohort_actives.append([])
    for nweeks in range(0, max_weeks):
        nusers = active.get(nweeks, 0)
        pusers = nusers / tusers
        cohort_actives[-1].append(pusers)


# Fold the retentions distributions together.
# ===========================================

weeks = defaultdict(list)
for active in cohort_actives:
    for nweeks, pusers in enumerate(active):
        weeks[nweeks].append(pusers)

for foo in sorted(weeks.items()):
    week, pusers = foo  # bug when unpacking in the for loop!?
    mean = sum(pusers) / len(pusers)
    print('{},{}'.format(week, mean))
