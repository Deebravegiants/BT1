# [H] Parse Server has an auth provider validation bypass on login via partial authData

## Summary
Severity: High
Advisory: GHSA-pfj7-wv7c-22pr
CVE: CVE-2026-33409
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-pfj7-wv7c-22pr
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.41
- npm: `parse-server` — affected >=0 <8.6.52

## Details
### Impact

An authentication bypass vulnerability allows an attacker to log in as any user who has linked a third-party authentication provider, without knowing the user's credentials. The attacker only needs to know the user's provider ID to gain full access to their account, including a valid session token.

This affects Parse Server deployments where the server option `allowExpiredAuthDataToken` is set to `true`. The default value is `false`.

### Patches

Auth providers are now always validated on login, regardless of the `allowExpiredAuthDataToken` setting. The option `allowExpiredAuthDataToken` has been deprecated and will be removed in a future major version.

### Workarounds

Set `allowExpiredAuthDataToken` to `false` (the default) or remove the option from the server configuration.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-pfj7-wv7c-22pr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33409
- https://github.com/parse-community/parse-server/pull/10246
- https://github.com/parse-community/parse-server/pull/10247
- https://github.com/parse-community/parse-server/commit/8d7df5639c4a35768fe8b78b4580b30e8a74721c
- https://github.com/parse-community/parse-server/commit/98f4ba5bcf2c199bfe6225f672e8edcd08ba732d
- https://github.com/parse-community/parse-server
