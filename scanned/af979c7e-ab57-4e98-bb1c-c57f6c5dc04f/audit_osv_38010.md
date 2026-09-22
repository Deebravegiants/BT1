# [M] Emlog: CSRF in Backend Upgrade Interface Leading to Arbitrary Remote SQL Execution and Arbitrary File Write

## Summary
Severity: Medium
Advisory: CVE-2026-34228
Aliases: GHSA-2rcc-jg83-34vp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34228
Type: osv

## Details
Emlog is an open source website building system. Prior to version 2.6.8, the backend upgrade interface accepts remote SQL and ZIP URLs via GET parameters. The server first downloads and executes the SQL file, then downloads the ZIP file and extracts it directly into the web root directory. This process does not validate a CSRF token. Therefore, an attacker only needs to trick an authenticated administrator into visiting a malicious link to achieve arbitrary SQL execution and arbitrary file write. This issue has been patched in version 2.6.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34228.json
- https://github.com/emlog/emlog/security/advisories/GHSA-2rcc-jg83-34vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34228
- https://github.com/emlog/emlog/commit/4c3b8f3486e2c9caafee38a5eedb3cd16f8c8d6f
