# [C] pgAdmin 4 Vulnerable to Cross-Site Scripting (XSS) via Query Result Rendering

## Summary
Severity: Critical
Advisory: GHSA-2rrx-pphc-qfv9
CVE: CVE-2025-2946
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2025-04-03
Source: https://github.com/advisories/GHSA-2rrx-pphc-qfv9
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.2

## Details
pgAdmin <= 9.1 is affected by a security vulnerability with Cross-Site Scripting(XSS). If attackers execute any arbitrary HTML/JavaScript in a user's browser through query result rendering, then HTML/JavaScript runs on the browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2946
- https://github.com/pgadmin-org/pgadmin4/issues/8602
- https://github.com/pgadmin-org/pgadmin4/commit/1305d9910beefd0d6b4c7eb4f111f86edb1d356b
- https://github.com/pgadmin-org/pgadmin4
