# [M] Deciso OPNsense diag_backup.php filename Directory Traversal Arbitrary File Creation Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-13698
CVSS: 4.5 (CVSS:3.0/AV:A/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-13698
Type: osv

## Details
Deciso OPNsense diag_backup.php filename Directory Traversal Arbitrary File Creation Vulnerability. This vulnerability allows network-adjacent attackers to create arbitrary files on affected installations of Deciso OPNsense. Authentication is required to exploit this vulnerability.

The specific flaw exists within the handling of backup configuration files. The issue results from the lack of proper validation of a user-supplied path prior to using it in file operations. An attacker can leverage this vulnerability to create files in the context of root. Was ZDI-CAN-28133.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13698.json
- https://github.com/opnsense/core/commit/cb15c935137d05c86a1e6cf12af877e9c32a23af
- https://nvd.nist.gov/vuln/detail/CVE-2025-13698
- https://www.zerodayinitiative.com/advisories/ZDI-25-1022/
