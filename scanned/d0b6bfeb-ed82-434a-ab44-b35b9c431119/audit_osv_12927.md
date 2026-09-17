# [M] CVE-2018-16392

## Summary
Severity: Medium
Advisory: CVE-2018-16392
CVSS: 6.8 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16392
Type: osv

## Details
Several buffer overflows when handling responses from a TCOS Card in tcos_select_file in libopensc/card-tcos.c in OpenSC before 0.19.0-rc1 could be used by attackers able to supply crafted smartcards to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00009.html
- https://access.redhat.com/errata/RHSA-2019:2154
- https://github.com/OpenSC/OpenSC/releases/tag/0.19.0-rc1
- https://github.com/OpenSC/OpenSC/commit/360e95d45ac4123255a4c796db96337f332160ad#diff-b2a356323a9ff2024d041cf2d7e89dd3
- https://www.x41-dsec.de/lab/advisories/x41-2018-002-OpenSC/
