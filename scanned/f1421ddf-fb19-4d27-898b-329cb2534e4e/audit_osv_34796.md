# [M] Insecure Direct Object Reference (IDOR) Allows Unauthorized Deletion of User Collections

## Summary
Severity: Medium
Advisory: CVE-2025-65097
Aliases: GHSA-v7c8-f6xc-rv9g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:L/SA:N)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2025-65097
Type: osv

## Details
RomM (ROM Manager) allows users to scan, enrich, browse and play their game collections with a clean and responsive interface. Prior to 4.4.1 and 4.4.1-beta.2, an Authenticated User can delete collections belonging to other users by directly sending a DELETE request to the collection endpoint. No ownership verification is performed before deleting collections. This vulnerability is fixed in 4.4.1 and 4.4.1-beta.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65097.json
- https://github.com/rommapp/romm/security/advisories/GHSA-v7c8-f6xc-rv9g
- https://nvd.nist.gov/vuln/detail/CVE-2025-65097
