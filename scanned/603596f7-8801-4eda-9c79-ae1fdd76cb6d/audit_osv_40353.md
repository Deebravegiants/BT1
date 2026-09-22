# [H] net/sched: taprio: fix use-after-free in advance_sched() on schedule switch

## Summary
Severity: High
Advisory: CVE-2026-53011
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53011
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: taprio: fix use-after-free in advance_sched() on schedule switch

In advance_sched(), when should_change_schedules() returns true,
switch_schedules() is called to promote the admin schedule to oper.
switch_schedules() queues the old oper schedule for RCU freeing via
call_rcu(), but 'next' still points into an entry of the old oper
schedule. The subsequent 'next->end_time = end_time' and
rcu_assign_pointer(q->current_entry, next) are use-after-free.

Fix this by selecting 'next' from the new oper schedule immediately
after switch_schedules(), and using its pre-calculated end_time.
setup_first_end_time() sets the first entry's end_time to
base_time + interval when the schedule is installed, so the value
is already correct.

The deleted 'end_time = sched_base_time(admin)' assignment was also
harmful independently: it would overwrite the new first entry's
pre-calculated end_time with just base_time.

## References
- https://git.kernel.org/stable/c/0e62171df8ed4804d00db088f17eed06468233fa
- https://git.kernel.org/stable/c/105425b1969c5affe532713cfac1c0b320d7ac2b
- https://git.kernel.org/stable/c/1bd286fa3e21200133478ed523cc6a2788baf38a
- https://git.kernel.org/stable/c/3471874578160a28c171a607fa069f24062634b8
- https://git.kernel.org/stable/c/7256996e1ef553716817f3bfd077c2f3b48b582f
- https://git.kernel.org/stable/c/a8fc396519ef4f081bc545e88f61241728bb78d7
- https://git.kernel.org/stable/c/b73235da5dde77ed1264f9767b62c28c9d71fd78
- https://git.kernel.org/stable/c/eee072fe16c646190d33ae69c9983d8de1562bf8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53011.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53011
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
