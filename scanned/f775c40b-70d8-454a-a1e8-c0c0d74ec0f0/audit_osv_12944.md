# [M] CVE-2018-16427

## Summary
Severity: Medium
Advisory: CVE-2018-16427
CVSS: 4.3 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-16427
Type: osv

## Details
Various out of bounds reads when handling responses in OpenSC before 0.19.0-rc1 could be used by attackers able to supply crafted smartcards to potentially crash the opensc library using programs.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00009.html
- https://access.redhat.com/errata/RHSA-2019:2154
- https://www.x41-dsec.de/lab/advisories/x41-2018-002-OpenSC/
- https://github.com/OpenSC/OpenSC/pull/1447/commits/8fe377e93b4b56060e5bbfb6f3142ceaeca744fa
- https://github.com/OpenSC/OpenSC/releases/tag/0.19.0-rc1
