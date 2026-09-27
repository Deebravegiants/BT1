# [C] Ajenti has a potential Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-27975
Aliases: GHSA-vcw3-r3fx-j444
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27975
Type: osv

## Details
Ajenti is a Linux and BSD modular server admin panel. Prior to version 2.2.13, an unauthenticated user could gain access to a server to execute arbitrary code on this server. This is fixed in the version 2.2.13.

## References
- https://github.com/ajenti/ajenti/releases/tag/v2.2.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27975.json
- https://github.com/ajenti/ajenti/security/advisories/GHSA-vcw3-r3fx-j444
- https://nvd.nist.gov/vuln/detail/CVE-2026-27975
