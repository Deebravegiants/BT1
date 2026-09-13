# [H] sched/fair: Fix NEXT_BUDDY

## Summary
Severity: High
Advisory: CVE-2024-49573
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-49573
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched/fair: Fix NEXT_BUDDY

Adam reports that enabling NEXT_BUDDY insta triggers a WARN in
pick_next_entity().

Moving clear_buddies() up before the delayed dequeue bits ensures
no ->next buddy becomes delayed. Further ensure no new ->next buddy
ever starts as delayed.

## References
- https://git.kernel.org/stable/c/493afbd187c4c9cc1642792c0d9ba400c3d6d90d
- https://git.kernel.org/stable/c/5dbe6816c49197677a5ecce749bd99929da147da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49573.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49573
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
