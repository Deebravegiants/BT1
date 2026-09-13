# [C] SiYuan before 3.8.1 Local Privilege Escalation via Uncontrolled Search Path

## Summary
Severity: Critical
Advisory: CVE-2026-82649
Aliases: GHSA-9j65-967f-5rv3
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82649
Type: osv

## Details
SiYuan Windows installer before version 3.8.1 (affected versions >= 2.0.14) contains an uncontrolled search path element vulnerability in its NSIS installer, which invokes system executables such as TASKKILL by name rather than by absolute path. Because NSIS nsExec::Exec resolves these calls using a search path that includes the installer's own launch directory ahead of System32, an attacker who plants a malicious executable (e.g., a renamed TASKKILL.exe) in that directory can have it executed when the installer runs. These calls occur in electron-builder's preInit hook before the license page is displayed, and with an all-users (elevated) install the planted binary executes with an elevated token, resulting in local privilege escalation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82649.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-9j65-967f-5rv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-82649
- https://www.vulncheck.com/advisories/siyuan-before-3.8.1-local-privilege-escalation-via-uncontrolled-search-path
- https://github.com/siyuan-note/siyuan/commit/251596fc0de2f9528c00c224252fd073a99973f4
