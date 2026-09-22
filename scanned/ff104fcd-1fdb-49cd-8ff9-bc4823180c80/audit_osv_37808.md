# [M] solidtime vulnerable to IDOR in private projects

## Summary
Severity: Medium
Advisory: CVE-2026-33345
Aliases: GHSA-354j-rx28-jjxm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33345
Type: osv

## Details
solidtime is an open-source time-tracking app. Prior to version 0.11.6, the project detail endpoint GET /api/v1/organizations/{org}/projects/{project} allows any authenticated Employee to access any project in the organization by UUID, including private projects they are not a member of. The index() endpoint correctly applies the visibleByEmployee() scope, but show() does not. This issue has been patched in version 0.11.6.

## References
- https://github.com/solidtime-io/solidtime/releases/tag/v0.11.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33345.json
- https://github.com/solidtime-io/solidtime/security/advisories/GHSA-354j-rx28-jjxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33345
- https://github.com/solidtime-io/solidtime/commit/192c8c3b887aab34117b983c687934ca7c305209
