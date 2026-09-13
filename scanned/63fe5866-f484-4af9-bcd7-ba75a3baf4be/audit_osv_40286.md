# [H] Wekan: OIDC Account Takeover via Unconditional Email-Based Account Merge in onCreateUser hook

## Summary
Severity: High
Advisory: CVE-2026-52893
Aliases: GHSA-mp7g-hj5q-gxhq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-52893
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.32, the Wekan Accounts.onCreateUser hook in server/models/users.js merges OIDC logins into existing accounts when the OIDC email or username matches an existing Wekan user, without verifying ownership or checking email_verified. An attacker using an OIDC provider account with a victim's email or username can cause Wekan to merge the attacker's OIDC credentials into the victim account and then log in as that account. This issue is fixed in version 9.32.

## References
- https://github.com/wekan/wekan/releases/tag/v9.32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52893.json
- https://github.com/wekan/wekan/security/advisories/GHSA-mp7g-hj5q-gxhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-52893
- https://github.com/wekan/wekan/commit/73204d4e0a7d77a1b186b3d76e8eaf2f3e7c9fd9
