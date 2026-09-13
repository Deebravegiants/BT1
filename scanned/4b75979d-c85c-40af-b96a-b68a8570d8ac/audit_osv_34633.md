# [M] LinkAce: Data Exfiltration via Export Functions Allow Access to All Users' Private Links

## Summary
Severity: Medium
Advisory: CVE-2025-62720
Aliases: GHSA-cqxv-6v28-2f2h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-11-04
Source: https://osv.dev/vulnerability/CVE-2025-62720
Type: osv

## Details
LinkAce is a self-hosted archive to collect website links. Versions 2.3.1 and below allow any authenticated user to export the entire database of links from all users in the system, including private links that should only be accessible to their owners. The HTML and CSV export functions in the ExportController class retrieve all links without applying any ownership or visibility filtering, effectively bypassing all access controls implemented elsewhere in the application. This issue is fixed in version 2.4.0.

## References
- https://github.com/Kovah/LinkAce/releases/tag/v2.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62720.json
- https://github.com/Kovah/LinkAce/security/advisories/GHSA-cqxv-6v28-2f2h
- https://nvd.nist.gov/vuln/detail/CVE-2025-62720
- https://github.com/Kovah/LinkAce/commit/0ba49dba5176db390999de1f90b9d743a4aedc24
