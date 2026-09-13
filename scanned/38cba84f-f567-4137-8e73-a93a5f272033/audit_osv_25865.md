# [C] Potential account take over due to unverified emails from Microsoft Identity Platform

## Summary
Severity: Critical
Advisory: CVE-2023-46241
Aliases: GHSA-2w32-w539-3m7r
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2023-46241
Type: osv

## Details
`discourse-microsoft-auth` is a plugin that enables authentication via Microsoft. On sites with the `discourse-microsoft-auth` plugin enabled, an attack can potentially take control of a victim's Discourse account. Sites that have configured their application's account type to any options other than `Accounts in this organizational directory only (O365 only - Single tenant)` are vulnerable. This vulnerability has been patched in commit c40665f44509724b64938c85def9fb2e79f62ec8 of `discourse-microsoft-auth`. A `microsoft_auth:revoke` rake task has also been added which will deactivate and log out all users that have connected their accounts to Microsoft. User API keys as well as API keys created by those users will also be revoked. The rake task will also remove the connection records to Microsoft for those users. This will allow affected users to re-verify their account emails as well as reconnect their Discourse account to Microsoft for authentication. As a workaround, disable the `discourse-microsoft-auth` plugin by setting the `microsoft_auth_enabled` site setting to `false`. Run the `microsoft_auth:log_out_users` rake task to log out all users with associated Microsoft accounts.

## References
- https://learn.microsoft.com/en-us/security/zero-trust/develop/identity-supported-account-types
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46241.json
- https://github.com/discourse/discourse-microsoft-auth/security/advisories/GHSA-2w32-w539-3m7r
- https://nvd.nist.gov/vuln/detail/CVE-2023-46241
- https://github.com/discourse/discourse-microsoft-auth/commit/c40665f44509724b64938c85def9fb2e79f62ec8
