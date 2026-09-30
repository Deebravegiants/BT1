# [H] CVE-2021-44686

## Summary
Severity: High
Advisory: CVE-2021-44686
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-12-07
Source: https://osv.dev/vulnerability/CVE-2021-44686
Type: osv

## Details
calibre before 5.32.0 contains a regular expression that is vulnerable to ReDoS (Regular Expression Denial of Service) in html_preprocess_rules in ebooks/conversion/preprocess.py.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W7QKFPYJ23KG6WJ5NIYAM4N2NWZCLQGL/
- https://bugs.launchpad.net/calibre/+bug/1951979
- https://github.com/dwisiswant0/advisory/issues/18
- https://github.com/kovidgoyal/calibre/compare/v5.31.1...v5.32.0
