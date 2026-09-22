# [M] Papra: Cross-organization tag deletion and modification via authenticated cross-tenant request

## Summary
Severity: Medium
Advisory: CVE-2026-48052
Aliases: GHSA-wrx4-3vff-jm94
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-48052
Type: osv

## Details
Papra is a minimalistic document management and archiving platform. Prior to version 26.5.0, an authenticated user who is a member of any organization can delete or rename tags belonging to a different organization, given the target tag's ID. The route handler verifies the caller's membership of the ":organizationId" in the URL, but the repository write filters on tag.id alone, so the URL-level org scope never reaches the database. This issue has been patched in version 26.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48052.json
- https://github.com/papra-hq/papra/security/advisories/GHSA-wrx4-3vff-jm94
- https://nvd.nist.gov/vuln/detail/CVE-2026-48052
- https://github.com/papra-hq/papra/commit/47d44e0681bf59da0638b140d1c5ef5b970f6b67
- https://github.com/papra-hq/papra/pull/1080
