# [C] Mautic allows Remote Code Execution and File Deletion in Asset Uploads

## Summary
Severity: Critical
Advisory: GHSA-73gx-x7r9-77x2
CVE: CVE-2024-47051
CWE: CWE-23, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2025-02-26
Source: https://github.com/advisories/GHSA-73gx-x7r9-77x2
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <5.2.3

## Details
### Summary
This advisory addresses two critical security vulnerabilities present in Mautic versions before 5.2.3.  These vulnerabilities could be exploited by authenticated users.

* **Remote Code Execution (RCE) via Asset Upload:**  A Remote Code Execution vulnerability has been identified in the asset upload functionality. Insufficient enforcement of allowed file extensions allows an attacker to bypass restrictions and upload executable files, such as PHP scripts.

* **Path Traversal File Deletion:** A Path Traversal vulnerability exists in the upload validation process.  Due to improper handling of path components, an authenticated user can manipulate the file deletion process to delete arbitrary files on the host system. 
  
### Mitigation
Please update to 5.2.3 or later.

### Workarounds
None

### References
https://owasp.org/www-community/attacks/Code_Injection
https://owasp.org/www-community/attacks/Path_Traversal

If you have any questions or comments about this advisory:

Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-73gx-x7r9-77x2
- https://nvd.nist.gov/vuln/detail/CVE-2024-47051
- https://github.com/mautic/mautic/commit/75bc488ce98b9c8ec01114984049fc1c42c0cae5
- https://github.com/mautic/mautic
- https://owasp.org/www-community/attacks/Code_Injection
- https://owasp.org/www-community/attacks/Path_Traversal
