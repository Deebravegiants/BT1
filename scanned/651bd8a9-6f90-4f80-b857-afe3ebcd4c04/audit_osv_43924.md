# [C] OS Command Injection in PayRange API

## Summary
Severity: Critical
Advisory: CVE-2026-76060
Aliases: GHSA-88m4-hrgp-m9v3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-76060
Type: osv

## Details
An authenticated OS command injection vulnerability exists in ZoneMinder's event export functionality. The exportFile HTTP request parameter is passed unsanitized into a shell command executed via PHP's exec(), allowing any authenticated user with View Events permission to execute arbitrary operating system commands on the server.

## References
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2026/icsa-26-237-02.json
- https://zoneminder.com/downloads
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76060.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-88m4-hrgp-m9v3
- https://nvd.nist.gov/vuln/detail/CVE-2026-76060
- https://www.cisa.gov/news-events/ics-advisories/icsa-26-237-02
- https://github.com/ZoneMinder/zoneminder
