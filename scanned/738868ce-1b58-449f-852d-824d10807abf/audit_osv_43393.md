# [H] Trigger.dev: Account Takeover via Cross-Provider OAuth Email Matching in Google Login

## Summary
Severity: High
Advisory: CVE-2026-73655
Aliases: GHSA-rp8c-h4xr-w9qv
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73655
Type: osv

## Details
Trigger.dev is a platform for building and deploying fully managed AI agents and workflows. Prior to 4.5.2, addGoogleStrategy() in apps/webapp/app/services/googleAuth.server.ts passes a Google profile email to findOrCreateGoogleUser() in apps/webapp/app/models/user.server.ts without requiring Google's email_verified assertion. When existingEmailUser && !existingUser is true, the flow writes the new Google authIdentifier into the existing email-matched account and returns that user object, allowing an attacker-controlled Google profile with an unverified matching email to take over the account. This issue is fixed in version 4.5.2.

## References
- https://github.com/triggerdotdev/trigger.dev/releases/tag/v4.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73655.json
- https://github.com/triggerdotdev/trigger.dev/security/advisories/GHSA-rp8c-h4xr-w9qv
- https://nvd.nist.gov/vuln/detail/CVE-2026-73655
- https://github.com/triggerdotdev/trigger.dev/commit/34b1a181c2a1d33a53ebab88f84b05f81fea4254
- https://github.com/triggerdotdev/trigger.dev/pull/4199
