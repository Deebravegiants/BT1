# [M] AnythingLLM: Password recovery accepts one recovery code twice after whitespace normalization

## Summary
Severity: Medium
Advisory: CVE-2026-72917
Aliases: GHSA-vv8w-wg6r-hq56
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72917
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. From 1.0.0 to 1.15.0, AnythingLLM's unauthenticated account-recovery flow in server/utils/PasswordRecovery/index.js uses recoverAccount() to deduplicate the raw recoveryCodes values before trimming them, so one valid code submitted twice with different surrounding whitespace can satisfy the two-code check. Each normalized value can also match the same stored hash instead of consuming a distinct hash. An attacker who knows the target username and one recovery code can call POST /api/system/recover-account in multi-user mode, receive a password-reset token, and use POST /api/system/reset-password to take over the account, including an administrator account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72917.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-vv8w-wg6r-hq56
- https://nvd.nist.gov/vuln/detail/CVE-2026-72917
- https://github.com/Mintplex-Labs/anything-llm/commit/61766d06b77b903f66dc4afd8dffb3a39012db14
