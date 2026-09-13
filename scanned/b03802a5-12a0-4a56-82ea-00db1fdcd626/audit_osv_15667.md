# [C] CVE-2019-18604

## Summary
Severity: Critical
Advisory: CVE-2019-18604
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/CVE-2019-18604
Type: osv

## Details
In axohelp.c before 1.3 in axohelp in axodraw2 before 2.1.1b, as distributed in TeXLive and other collections, sprintf is mishandled.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00033.html
- https://github.com/TeX-Live/texlive-source/commit/9216833a3888a4105a18e8c349f65b045ddb1079#diff-987e40c0e27ee43f6a2414ada73a191a
