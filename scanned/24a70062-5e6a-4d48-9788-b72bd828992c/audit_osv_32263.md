# [C] Path Traversal endpoint 'exportar_dump.php' parameter 'file' in WeGIA

## Summary
Severity: Critical
Advisory: CVE-2025-26616
Aliases: GHSA-xxqg-p22h-3f32
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26616
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. A Path Traversal vulnerability was discovered in the WeGIA application, `exportar_dump.php` endpoint. This vulnerability could allow an attacker to gain unauthorized access to sensitive information stored in `config.php`. `config.php` contains information that could allow direct access to the database. This issue has been addressed in version 3.2.14 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26616.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-xxqg-p22h-3f32
- https://nvd.nist.gov/vuln/detail/CVE-2025-26616
