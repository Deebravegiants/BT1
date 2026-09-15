# [M] Directus: Sensitive fields exposed in revision history

## Summary
Severity: Medium
Advisory: GHSA-mvv8-v4jj-g47j
CVE: CVE-2026-39943
CWE: CWE-200, CWE-312
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-mvv8-v4jj-g47j
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.17.0

## Details
### Summary

Directus stores revision records (in `directus_revisions`) whenever items are created or updated. Due to the revision snapshot code not consistently calling the `prepareDelta` sanitization pipeline, sensitive fields (including user tokens, two-factor authentication secrets, external auth identifiers, auth data, stored credentials, and AI provider API keys) could be stored in plaintext within revision records.

### Impact
Any user or service account with read access to `directus_revisions` (or flow logs) could retrieve values for fields that are supposed to be concealed or encrypted at rest, including:
- `token`, `tfa_secret`, `external_identifier`, `auth_data`, `credentials`
- `ai_openai_api_key`, `ai_anthropic_api_key`, `ai_google_api_key`, `ai_openai_compatible_api_key`

This could lead to account takeover (via stolen tokens or 2FA secrets) or unauthorized use of third-party API keys stored against users.

### Affected code paths

1. **Item create/update revisions** The data (snapshot) field written to directus_revisions was not processed through prepareDelta, so concealed/encrypted fields were stored without redaction. Relational fields were also included, which should have been excluded.
2. **Authentication service** When a user was auto-suspended after repeated failed login attempts, the revision record was created with the raw user object (including all sensitive fields) rather than the sanitized delta.

## References
- https://github.com/directus/directus/security/advisories/GHSA-mvv8-v4jj-g47j
- https://nvd.nist.gov/vuln/detail/CVE-2026-39943
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v11.17.0
