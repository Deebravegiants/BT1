# [C] FreePBX Post-Authenticated Command Injection

## Summary
Severity: Critical
Advisory: CVE-2025-55211
Aliases: GHSA-xg83-m6q5-q24h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U/AU:N/R:U/V:D/RE:L/U:Green)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-55211
Type: osv

## Details
FreePBX is an open-source web-based graphical user interface. From 17.0.19.11 to before 17.0.21, authenticated users of the Administrator Control Panel (ACP) can run arbitrary shell commands by maliciously changing languages of the framework module. This vulnerability is fixed in 17.0.21.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55211.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-xg83-m6q5-q24h
- https://nvd.nist.gov/vuln/detail/CVE-2025-55211
