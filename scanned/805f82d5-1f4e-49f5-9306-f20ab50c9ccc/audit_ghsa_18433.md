# [M] Aim vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-gmvv-rj92-9w35
CVE: CVE-2025-51464
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-07-22
Source: https://github.com/advisories/GHSA-gmvv-rj92-9w35
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
Cross-site Scripting (XSS) in aimhubio Aim 3.28.0 allows remote attackers to execute arbitrary JavaScript in victims browsers via malicious Python code submitted to the /api/reports endpoint, which is interpreted and executed by Pyodide when the report is viewed. No sanitisation or sandbox restrictions prevent JavaScript execution via pyodide.code.run_js().

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51464
- https://github.com/aimhubio/aim/pull/3333
- https://github.com/aimhubio/aim
- https://www.gecko.security/blog/cve-2025-51464
