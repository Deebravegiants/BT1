# [H] Calibre Web and Autocaliweb have a ReDoS vulnerability

## Summary
Severity: High
Advisory: GHSA-2g7m-ph9x-7q7m
CVE: CVE-2025-6998
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-24
Source: https://github.com/advisories/GHSA-2g7m-ph9x-7q7m
Type: github-advisory

## Affected
- PyPI: `calibreweb` — affected >=0

## Details
ReDoS in strip_whitespaces() function in cps/string_helper.py in Calibre Web and Autocaliweb allows unauthenticated remote attackers to cause denial of service via specially crafted username parameter that triggers catastrophic backtracking during login. This issue affects Calibre Web: 0.6.24 (Nicolette); Autocaliweb: from 0.7.0 before 0.7.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6998
- https://fluidattacks.com/advisories/megadeth
- https://github.com/gelbphoenix/autocaliweb
- https://github.com/janeczku/calibre-web
