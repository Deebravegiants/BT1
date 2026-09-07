# [M] PyDio Stored XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5ghg-233h-7j79
CVE: CVE-2019-10047
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5ghg-233h-7j79
Type: github-advisory

## Affected
- PyPI: `pydio` — affected >=0

## Details
A stored XSS vulnerability exists in the web application of Pydio through 8.2.2 that can be exploited by levering the file upload and file preview features of the application. An authenticated attacker can upload an HTML file containing JavaScript code and afterwards a file preview URL can be used to access the uploaded file. If a malicious user shares an uploaded HTML file containing JavaScript code with another user of the application, and tricks an authenticated victim into accessing a URL that results in the HTML code being interpreted by the web browser, then the included JavaScript code is executed under the context of the victim user session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10047
- https://github.com/mwiatrzyk/pydio
- https://packetstormsecurity.com/files/152292/Pydio-8-Command-Execution-Cross-Site-Scripting.html
- https://www.secureauth.com/labs/advisories/pydio-8-multiple-vulnerabilities
