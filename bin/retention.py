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

distributions = []
for date, users in sorted(cohorts.items()):

    distribution = defaultdict(int)
    for username in users:
        start, end = usermap[username]
        nweeks = (end - start).days // 7
        for n in range(nweeks, -1, -1):
            distribution[n] += 1

    max_weeks = max(distribution.keys())
    tusers = len(users)

    distributions.append([tusers, []])
    for nweeks in range(0, max_weeks+1):
        nusers = distribution.get(nweeks, 0)
        pusers = nusers / tusers
        distributions[-1][1].append((pusers, nusers))


# Fold the retentions distributions together.
# ===========================================

def fold(distributions):
    weeks = defaultdict(list)
    for distribution in distributions:
        for nweeks, (pusers, nusers, tusers) in enumerate(distribution):
            weeks[nweeks].append(pusers)

    values = []
    for foo in sorted(weeks.items()):
        week, pusers = foo  # bug when unpacking in the for loop!?
        mean = sum(pusers) / len(pusers)
        values.append(mean)

    return values


for tusers, distribution in distributions:
    print('{},'.format(tusers), end='')
    print(','.join(['{}'.format(p) for p,n in distribution]))


raise SystemExit


ndist = len(distributions)
one_third = ndist // 3
two_thirds = one_third * 2

early = distributions[:one_third]
middle = distributions[one_third:two_thirds]
late = distributions[two_thirds:]

distgroups = [early, middle, late]

for distributions in distgroups:
    print(','.join(['{}'.format(p) for p in fold(distributions)]))
