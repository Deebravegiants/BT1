# [M] CVE-2018-18897

## Summary
Severity: Medium
Advisory: CVE-2018-18897
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-02
Source: https://osv.dev/vulnerability/CVE-2018-18897
Type: osv

## Details
An issue was discovered in Poppler 0.71.0. There is a memory leak in GfxColorSpace::setDisplayProfile in GfxState.cc, as demonstrated by pdftocairo.

## References
- https://access.redhat.com/errata/RHSA-2019:2022
- https://access.redhat.com/errata/RHSA-2019:2713
- https://lists.debian.org/debian-lts-announce/2022/09/msg00030.html
- https://usn.ubuntu.com/4042-1/
- https://gitlab.freedesktop.org/poppler/poppler/issues/654
