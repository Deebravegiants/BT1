# [M] Directus's conceal fields are searchable if read permissions enabled

## Summary
Severity: Medium
Advisory: GHSA-8jpw-gpr4-8cmh
CVE: CVE-2025-64748
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-8jpw-gpr4-8cmh
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.13.0
- npm: `@directus/api` — affected >=0 <32.0.0

## Details
## Summary

A vulnerability allows authenticated users to search concealed/sensitive fields when they have read permissions. While actual values remain masked (`****`), successful matches can be detected through returned records, enabling enumeration attacks on sensitive data.

## Details

The system permits search operations on concealed fields in the `directus_users` collection, including `token`, `tfa_secret`, `password`. Matching records are returned with masked values, but their presence confirms the searched value exists.

The "Recommended Defaults" for "App Access" grant users full read permissions to their role/user records, inadvertently enabling them to search for any user's tokens, TFA secrets, and password hashes. Attackers can leverage known password hashes from breach databases to identify accounts with compromised passwords.

# Impact

This vulnerability enables:
- **Token enumeration** - Verification of valid authentication tokens
- **Password hash matching** - Identification of accounts using known compromised passwords
- **Information disclosure** - Confirmation of sensitive value existence without viewing actual data
- **Increased attack surface** - Default permissions automatically expose all deployments using recommended settings

The risk is particularly high for password fields, where attackers can cross-reference publicly available hash databases to identify vulnerable accounts.

## References
- https://github.com/directus/directus/security/advisories/GHSA-8jpw-gpr4-8cmh
- https://nvd.nist.gov/vuln/detail/CVE-2025-64748
- https://github.com/directus/directus/commit/7737d56e096f95edfbdf861a3c08999ad31ce204
- https://github.com/directus/directus
