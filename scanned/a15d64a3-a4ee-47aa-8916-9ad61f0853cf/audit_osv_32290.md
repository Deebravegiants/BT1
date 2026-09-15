# [C] WeGIA vulnerable to OS Command Injection at endpoint 'importar_dump.php' parameter 'import' (RCE)

## Summary
Severity: Critical
Advisory: CVE-2025-27140
Aliases: GHSA-xw6w-x28r-2p5c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-24
Source: https://osv.dev/vulnerability/CVE-2025-27140
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. An OS Command Injection vulnerability was discovered in versions prior to 3.2.15 of the WeGIA application, `importar_dump.php` endpoint. This vulnerability could allow an attacker to execute arbitrary code remotely. The command is basically a command to move a temporary file, so a webshell upload is also possible. Version 3.2.15 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27140.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-xw6w-x28r-2p5c
- https://nvd.nist.gov/vuln/detail/CVE-2025-27140
- https://github.com/LabRedesCefetRJ/WeGIA/commit/7d0df8c9a0b8b7d6862bbc23dc729d73e39672a1
