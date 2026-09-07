# [M] Calibre Web and Autocaliweb have OS Command Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qc4j-v7h6-xr5h
CVE: CVE-2025-7404
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-24
Source: https://github.com/advisories/GHSA-qc4j-v7h6-xr5h
Type: github-advisory

## Affected
- PyPI: `calibreweb` — affected >=0

## Details
Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in Calibre Web, Autocaliweb allows Blind OS Command Injection. This issue affects Calibre Web: 0.6.24 (Nicolette); Autocaliweb: from 0.7.0 before 0.7.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7404
- https://fluidattacks.com/advisories/kino
- https://github.com/gelbphoenix/autocaliweb
- https://github.com/janeczku/calibre-web
