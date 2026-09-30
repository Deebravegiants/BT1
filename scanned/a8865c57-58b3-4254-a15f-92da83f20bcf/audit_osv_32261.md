# [C] OS Command Injection endpoint 'gerenciar_backup.php' parameter 'file' (RCE) in WeGIA

## Summary
Severity: Critical
Advisory: CVE-2025-26613
Aliases: GHSA-g3w6-m6w8-p6r2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26613
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. An OS Command Injection vulnerability was discovered in the WeGIA application, `gerenciar_backup.php` endpoint. This vulnerability could allow an attacker to execute arbitrary code remotely. This issue has been addressed in version 3.2.14 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26613.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-g3w6-m6w8-p6r2
- https://nvd.nist.gov/vuln/detail/CVE-2025-26613
