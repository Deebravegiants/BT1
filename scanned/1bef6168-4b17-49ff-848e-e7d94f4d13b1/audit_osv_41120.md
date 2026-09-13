# [C] Search path without quotes in CivetWeb

## Summary
Severity: Critical
Advisory: CVE-2026-5789
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-5789
Type: osv

## Details
Vulnerability related to an unquoted search path in CivetWeb v1.16. This vulnerability allows a local attacker to execute arbitrary code with elevated privileges by placing a malicious executable in a directory that is scanned before the intended application path (C:\Program Files\CivetWeb\CivetWeb.exe --), due to the absence of quotes in the service configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5789.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5789
- https://www.incibe.es/en/incibe-cert/notices/aviso/search-path-without-quotes-civetweb
