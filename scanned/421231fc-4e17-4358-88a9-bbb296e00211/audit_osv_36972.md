# [C] CGI Parameter Injection (Bypass of STRICT_CGI_PARAMS and EscapeShellParam)

## Summary
Severity: Critical
Advisory: CVE-2026-27613
Aliases: GHSA-rfx5-fh9m-9jj9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27613
Type: osv

## Details
TinyWeb is a web server (HTTP, HTTPS) written in Delphi for Win32. A vulnerability in versions prior to 2.01 allows unauthenticated remote attackers to bypass the web server's CGI parameter security controls. Depending on the server configuration and the specific CGI executable in use, the impact is either source code disclosure or remote code execution (RCE). Anyone hosting CGI scripts (particularly interpreted languages like PHP) using vulnerable versions of TinyWeb is impacted. The problem has been patched in version 2.01. If upgrading is not immediately possible, ensure `STRICT_CGI_PARAMS` is enabled (it is defined by default in `define.inc`) and/or do not use CGI executables that natively accept dangerous command-line flags (such as `php-cgi.exe`). If hosting PHP, consider placing the server behind a Web Application Firewall (WAF) that explicitly blocks URL query string parameters that begin with a hyphen (`-`) or contain encoded double quotes (`%22`).

## References
- https://github.com/maximmasiutin/TinyWeb/releases/tag/v2.01
- https://www.masiutin.net/tinyweb-cve-2026-27613.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27613.json
- https://github.com/maximmasiutin/TinyWeb/security/advisories/GHSA-rfx5-fh9m-9jj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27613
- https://github.com/maximmasiutin/TinyWeb/commit/d9dbda8db49da69d2160e1c527e782b73b5ffb6b
