# [M] OpenProject: IDOR on OpenProject through /api/v3/documents/{id} via PATCH parameter "project_id" leads to Unauthorized Modification of Resources

## Summary
Severity: Medium
Advisory: CVE-2026-44732
Aliases: GHSA-mqvv-5mvc-7pg7
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-44732
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.2 and 17.4.0, OpenProject exposes a document update endpoint used to modify existing documents. The target document is loaded with visibility checks and then updated. During update, attacker-controlled attributes are applied to the persisted record before authorization is enforced. As a result, a user without :manage_documents in the source project can move and modify foreign project documents by setting project_id in a single PATCH request. This vulnerability is fixed in 17.3.2 and 17.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44732.json
- https://github.com/opf/openproject/security/advisories/GHSA-mqvv-5mvc-7pg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44732
