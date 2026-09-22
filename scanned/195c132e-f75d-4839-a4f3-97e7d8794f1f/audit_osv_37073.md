# [H] hoppscotch has IDOR in updateUserEnvironment / deleteUserEnvironment

## Summary
Severity: High
Advisory: CVE-2026-28216
Aliases: GHSA-72rv-vc3j-5vqr
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-28216
Type: osv

## Details
hoppscotch is an open source API development ecosystem. Prior to version 2026.2.0, any logged-in user can read, modify or delete another user's personal environment by ID. `user-environments.resolver.ts:82-109`, `updateUserEnvironment` mutation uses `@UseGuards(GqlAuthGuard)` but is missing the `@GqlUser()` decorator entirely. The user's identity is never extracted, so the service receives only the environment ID and performs a `prisma.userEnvironment.update({ where: { id } })` without any ownership filter. `deleteUserEnvironment` does extract the user but the service only uses the UID to check if the target is a global environment. Actual delete query uses WHERE { id } without AND userUid. hoppscotch environments store API keys, auth tokens and secrets used in API requests. An authenticated attacker who obtains another user's environment ID can read their secrets, replace them with malicious values or delete them entirely. The environment ID format is CUID, which limits mass exploitation but insider threat and combined info leak scenarios are realistic. Version 2026.2.0 fixes the issue.

## References
- https://github.com/hoppscotch/hoppscotch/releases/tag/2026.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28216.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-72rv-vc3j-5vqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-28216
