# [M] CVE-2021-47494

## Summary
Severity: Medium
Advisory: CVE-2021-47494
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47494
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

cfg80211: fix management registrations locking

The management registrations locking was broken, the list was
locked for each wdev, but cfg80211_mgmt_registrations_update()
iterated it without holding all the correct spinlocks, causing
list corruption.

Rather than trying to fix it with fine-grained locking, just
move the lock to the wiphy/rdev (still need the list on each
wdev), we already need to hold the wdev lock to change it, so
there's no contention on the lock in any case. This trivially
fixes the bug since we hold one wdev's lock already, and now
will hold the lock that protects all lists.

## References
- https://git.kernel.org/stable/c/4c22227e39c7a0b4dab55617ee8d34d171fab8d4
- https://git.kernel.org/stable/c/09b1d5dc6ce1c9151777f6c4e128a59457704c97
- https://git.kernel.org/stable/c/3c897f39b71fe68f90599f6a45b5f7bf5618420e
