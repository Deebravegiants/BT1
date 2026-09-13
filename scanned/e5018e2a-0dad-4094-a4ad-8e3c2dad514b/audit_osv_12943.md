# [M] CVE-2018-16426

## Summary
Severity: Medium
Advisory: CVE-2018-16426
CVSS: 4.3 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-16426
Type: osv

## Details
Endless recursion when handling responses from an IAS-ECC card in iasecc_select_file in libopensc/card-iasecc.c in OpenSC before 0.19.0-rc1 could be used by attackers able to supply crafted smartcards to hang or crash the opensc library using programs.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00009.html
- https://access.redhat.com/errata/RHSA-2019:2154
- https://github.com/OpenSC/OpenSC/commit/03628449b75a93787eb2359412a3980365dda49b#diff-f8c0128e14031ed9307d47f10f601b54
- https://github.com/OpenSC/OpenSC/releases/tag/0.19.0-rc1
- https://www.x41-dsec.de/lab/advisories/x41-2018-002-OpenSC/
