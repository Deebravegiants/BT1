# [H] CVE-2021-38562

## Summary
Severity: High
Advisory: CVE-2021-38562
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-18
Source: https://osv.dev/vulnerability/CVE-2021-38562
Type: osv

## Details
Best Practical Request Tracker (RT) 4.2 before 4.2.17, 4.4 before 4.4.5, and 5.0 before 5.0.2 allows sensitive information disclosure via a timing attack against lib/RT/REST2/Middleware/Auth.pm.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2JK57CEEXLQF7MGBCUX76DZHXML7LUSQ/
- https://docs.bestpractical.com/release-notes/rt/index.html
- https://lists.debian.org/debian-lts-announce/2022/06/msg00019.html
- https://github.com/bestpractical/rt/commit/70749bb66cb13dd70bd53340c371038a5f3ca57c
