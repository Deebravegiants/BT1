# [M] Parse Server affected by empty authData bypassing credential requirement on signup

## Summary
Severity: Medium
Advisory: GHSA-wjqw-r9x4-j59v
CVE: CVE-2026-33042
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-wjqw-r9x4-j59v
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.29
- npm: `parse-server` — affected >=0 <8.6.49

## Details
### Impact

A user can sign up without providing credentials by sending an empty `authData` object, bypassing the username and password requirement. This allows the creation of authenticated sessions without proper credentials, even when anonymous users are disabled.

### Patches

The fix ensures that empty or non-actionable `authData` is treated the same as absent `authData` for the purpose of credential validation on new user creation. Username and password are now required when no valid auth provider data is present.

### Workarounds

Use a Cloud Code `beforeSave` trigger on the `_User` class to reject signups where `authData` is empty and no username/password is provided.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-wjqw-r9x4-j59v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33042
- https://github.com/parse-community/parse-server/pull/10219
- https://github.com/parse-community/parse-server/pull/10220
- https://github.com/parse-community/parse-server
