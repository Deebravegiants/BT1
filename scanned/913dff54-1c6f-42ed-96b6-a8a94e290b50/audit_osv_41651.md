# [M] TREK: Cross-trip reservation title disclosure via file links

## Summary
Severity: Medium
Advisory: CVE-2026-62945
Aliases: GHSA-r4cp-666p-8f69
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-62945
Type: osv

## Details
TREK is a collaborative travel planner. Prior to 3.1.3, TREK file upload, update, and link actions accept attacker-controlled reservation_id, place_id, and assignment_id values without using findForeignLinkTarget() to verify that the referenced object belongs to the file's trip. An authenticated user with file-edit permission on any accessible trip can submit a foreign reservation identifier through POST /api/trips/:tripId/files/:id/link, POST /api/trips/:tripId/files, or PUT /api/trips/:tripId/files/:id. Subsequent reads through FILE_SELECT or getFileLinks() join the foreign reservation and return reservation_title, disclosing reservation existence and titles across private trip boundaries. This issue is fixed in version 3.1.3.

## References
- https://github.com/liketrek/TREK/releases/tag/v3.1.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62945.json
- https://github.com/liketrek/TREK/security/advisories/GHSA-r4cp-666p-8f69
- https://nvd.nist.gov/vuln/detail/CVE-2026-62945
- https://github.com/liketrek/TREK/commit/03cdb4d27689922460ba87085d04b426d4d40d26
- https://github.com/liketrek/TREK/pull/1324
