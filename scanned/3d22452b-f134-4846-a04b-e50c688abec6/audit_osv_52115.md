# [M] CVE-2021-47091

## Summary
Severity: Medium
Advisory: CVE-2021-47091
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47091
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac80211: fix locking in ieee80211_start_ap error path

We need to hold the local->mtx to release the channel context,
as even encoded by the lockdep_assert_held() there. Fix it.

## References
- https://git.kernel.org/stable/c/ac61b9c6c0549aaeb98194cf429d93c41bfe5f79
- https://git.kernel.org/stable/c/c1d1ec4db5f7264cfc21993e59e8f2dcecf4b44f
- https://git.kernel.org/stable/c/87a270625a89fc841f1a7e21aae6176543d8385c
