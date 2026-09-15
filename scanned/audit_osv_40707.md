# [M] TREK IDOR: any authenticated user can read another user's journey share token (full journey leak)

## Summary
Severity: Medium
Advisory: CVE-2026-54509
Aliases: GHSA-mx6m-qxv8-w624
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-54509
Type: osv

## Details
TREK is a collaborative travel planner. From 3.0.0 until 3.1.0, the GET /api/journeys/:id/share-link route in server/src/routes/journey.ts returns the result of getJourneyShareLink() from server/src/services/journeyShareService.ts without checking whether the authenticated requester can access the journey. Any ordinary authenticated user can enumerate sequential journey IDs and retrieve tokens from journey_share_tokens for another user's journey. The token grants unauthenticated access through GET /api/public/journey/:token to the shared journey's entries, captions, locations, moods, gallery photos, photo paths, and asset identifiers. This issue is fixed in version 3.1.0.

## References
- https://github.com/liketrek/TREK/releases/tag/v3.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54509.json
- https://github.com/liketrek/TREK/security/advisories/GHSA-mx6m-qxv8-w624
- https://nvd.nist.gov/vuln/detail/CVE-2026-54509
- https://github.com/liketrek/TREK/commit/ad893eb1cc75b6d56f402d73a6d41bd48ba7ae11
- https://github.com/liketrek/TREK/pull/1185
