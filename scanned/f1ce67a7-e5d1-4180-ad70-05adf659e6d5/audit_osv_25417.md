# [H] Out-of-bounds write in Linux kernel's net/sched: sch_qfq component

## Summary
Severity: High
Advisory: CVE-2023-3611
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-21
Source: https://osv.dev/vulnerability/CVE-2023-3611
Type: osv

## Details
An out-of-bounds write vulnerability in the Linux kernel's net/sched: sch_qfq component can be exploited to achieve local privilege escalation.

The qfq_change_agg() function in net/sched/sch_qfq.c allows an out-of-bounds write because lmax is updated according to packet sizes without bounds checks.

We recommend upgrading past commit 3e337087c3b5805fe0b8a46ba622a962880b5d64.

## References
- https://git.kernel.org
- https://kernel.dance/3e337087c3b5805fe0b8a46ba622a962880b5d64
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3611.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3611
- https://security.netapp.com/advisory/ntap-20230908-0002/
- https://www.debian.org/security/2023/dsa-5480
- https://www.debian.org/security/2023/dsa-5492
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3e337087c3b5805fe0b8a46ba622a962880b5d64
