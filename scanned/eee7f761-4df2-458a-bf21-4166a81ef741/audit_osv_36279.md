# [C] TinyWeb CGI Command Injection

## Summary
Severity: Critical
Advisory: CVE-2026-22781
Aliases: GHSA-m779-84h5-72q2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22781
Type: osv

## Details
TinyWeb is a web server (HTTP, HTTPS) written in Delphi for Win32. TinyWeb HTTP Server before version 1.98 is vulnerable to OS command injection via CGI ISINDEX-style query parameters. The query parameters are passed as command-line arguments to the CGI executable via Windows CreateProcess(). An unauthenticated remote attacker can execute arbitrary commands on the server by injecting Windows shell metacharacters into HTTP requests. This vulnerability is fixed in 1.98.

## References
- https://www.masiutin.net/tinyweb-cve-2025-cgi-command-injection.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22781.json
- https://github.com/maximmasiutin/TinyWeb/security/advisories/GHSA-m779-84h5-72q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-22781
- https://github.com/maximmasiutin/TinyWeb/commit/876b7e2887f4ea5be3e18bb2af7313f23a283c96
