# [M] CVE-2021-47382

## Summary
Severity: Medium
Advisory: CVE-2021-47382
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47382
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/qeth: fix deadlock during failing recovery

Commit 0b9902c1fcc5 ("s390/qeth: fix deadlock during recovery") removed
taking discipline_mutex inside qeth_do_reset(), fixing potential
deadlocks. An error path was missed though, that still takes
discipline_mutex and thus has the original deadlock potential.

Intermittent deadlocks were seen when a qeth channel path is configured
offline, causing a race between qeth_do_reset and ccwgroup_remove.
Call qeth_set_offline() directly in the qeth_do_reset() error case and
then a new variant of ccwgroup_set_offline(), without taking
discipline_mutex.

## References
- https://git.kernel.org/stable/c/0bfe741741327822d1482c7edef0184636d08b40
- https://git.kernel.org/stable/c/d2b59bd4b06d84a4eadb520b0f71c62fe8ec0a62
