# [C] Web-Check allows command Injection via Unvalidated URL in Screenshot API

## Summary
Severity: Critical
Advisory: CVE-2025-32778
Aliases: GHSA-5qg5-g7c2-pfx8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32778
Type: osv

## Details
Web-Check is an all-in-one OSINT tool for analyzing any website. A command injection vulnerability exists in the screenshot API of the Web Check project (Lissy93/web-check). The issue stems from user-controlled input (url) being passed unsanitized into a shell command using exec(), allowing attackers to execute arbitrary system commands on the underlying host. This could be exploited by sending crafted url parameters to extract files or even establish remote access. The vulnerability has been patched by replacing exec() with execFile(), which avoids using a shell and properly isolates arguments.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32778.json
- https://github.com/Lissy93/web-check/security/advisories/GHSA-5qg5-g7c2-pfx8
- https://nvd.nist.gov/vuln/detail/CVE-2025-32778
- https://github.com/Lissy93/web-check/commit/0e4958aa10b2650d32439a799f6fc83a7cd46cef
- https://github.com/Lissy93/web-check/pull/243
