# [H] CVE-2026-35535

## Summary
Severity: High
Advisory: CVE-2026-35535
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-35535
Type: osv

## Details
In Sudo through 1.9.17p2 before 3e474c2, a failure of a setuid, setgid, or setgroups call, during a privilege drop before running the mailer, is not a fatal error and can lead to privilege escalation.

## References
- https://bugs.debian.org/1130593
- https://bugs.launchpad.net/ubuntu/+source/sudo/+bug/2143042
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://lists.debian.org/debian-lts-announce/2026/06/msg00003.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-35535.json
- https://www.qualys.com/2026/03/10/crack-armor.txt
- https://access.redhat.com/errata/RHSA-2026:10758
- https://access.redhat.com/errata/RHSA-2026:11521
- https://access.redhat.com/errata/RHSA-2026:12310
- https://access.redhat.com/errata/RHSA-2026:13731
- https://access.redhat.com/errata/RHSA-2026:13888
- https://access.redhat.com/errata/RHSA-2026:13889
- https://access.redhat.com/errata/RHSA-2026:13891
- https://access.redhat.com/errata/RHSA-2026:13892
- https://access.redhat.com/errata/RHSA-2026:13895
- https://access.redhat.com/errata/RHSA-2026:13896
- https://access.redhat.com/errata/RHSA-2026:14228
- https://access.redhat.com/errata/RHSA-2026:14437
- https://access.redhat.com/errata/RHSA-2026:19067
- https://access.redhat.com/errata/RHSA-2026:19220
