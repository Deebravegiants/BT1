# [M] CVE-2018-16418

## Summary
Severity: Medium
Advisory: CVE-2018-16418
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-16418
Type: osv

## Details
A buffer overflow when handling string concatenation in util_acl_to_str in tools/util.c in OpenSC before 0.19.0-rc1 could be used by attackers able to supply crafted smartcards to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2019/09/msg00009.html
- https://access.redhat.com/errata/RHSA-2019:2154
- https://github.com/OpenSC/OpenSC/commit/360e95d45ac4123255a4c796db96337f332160ad#diff-628c8445c4e7ae92bbc4be08ba11a4c3
- https://github.com/OpenSC/OpenSC/releases/tag/0.19.0-rc1
- https://www.x41-dsec.de/lab/advisories/x41-2018-002-OpenSC/
