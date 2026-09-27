# [H] Hoppscotch: Cross-user private data exposure and UserHistory IDOR via team GraphQL resolvers

## Summary
Severity: High
Advisory: CVE-2026-69189
Aliases: GHSA-p25p-g9jp-7q46
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-69189
Type: osv

## Details
Hoppscotch is an open source API development ecosystem. Prior to 2026.6.0, the team, teamMembers.user, RESTHistory, GQLHistory, currentRESTSession, currentGQLSession, environments, globalEnvironments, and settings GraphQL paths expose another workspace member's private User data, while toggleHistoryStarStatus and removeRequestFromHistory in the UserHistory service accept another user's history identifier without enforcing userUid ownership, allowing an authenticated workspace member to read private request history, session data, request contents, authorization headers, environment values, and settings and to modify or delete the victim's private history entries. This issue is fixed in version 2026.6.0.

## References
- https://github.com/hoppscotch/hoppscotch/releases/tag/2026.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69189.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-p25p-g9jp-7q46
- https://nvd.nist.gov/vuln/detail/CVE-2026-69189
- https://github.com/hoppscotch/hoppscotch/commit/9cc980bc4feb1f8e139b23b9de0beed0db72d4b7
- https://github.com/hoppscotch/hoppscotch/pull/6409
