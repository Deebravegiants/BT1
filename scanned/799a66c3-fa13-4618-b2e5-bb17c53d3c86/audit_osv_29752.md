# [C] CVE-2024-46446

## Summary
Severity: Critical
Advisory: CVE-2024-46446
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-10-07
Source: https://osv.dev/vulnerability/CVE-2024-46446
Type: osv

## Details
Mecha CMS 3.0.0 is vulnerable to Directory Traversal. An attacker can construct cookies and URIs that bypass user identity checks. Parameters can then be passed through the POST method, resulting in the Deletion of Arbitrary Files or Website Takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46446.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46446
- https://github.com/Sp1d3rL1/Mecha-cms-Arbitrary-File-Deletion-Vulnerability
