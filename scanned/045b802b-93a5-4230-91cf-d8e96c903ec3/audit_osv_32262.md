# [C] Path Traversal endpoint 'examples.php' parameter 'src' in WeGIA

## Summary
Severity: Critical
Advisory: CVE-2025-26615
Aliases: GHSA-p5wx-pv8j-f96h
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26615
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. A Path Traversal vulnerability was discovered in the WeGIA application, `examples.php` endpoint. This vulnerability could allow an attacker to gain unauthorized access to sensitive information stored in `config.php`. `config.php` contains information that could allow direct access to the database. This issue has been addressed in version 3.2.14 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26615.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-p5wx-pv8j-f96h
- https://nvd.nist.gov/vuln/detail/CVE-2025-26615
