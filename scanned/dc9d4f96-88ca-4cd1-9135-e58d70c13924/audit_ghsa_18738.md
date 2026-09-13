# [M] Strapi Password Hashing is Missing Maximum Password Length Validation

## Summary
Severity: Medium
Advisory: GHSA-2cjv-6wg9-f4f3
CVE: CVE-2025-25298
CWE: CWE-261
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-2cjv-6wg9-f4f3
Type: github-advisory

## Affected
- npm: `@strapi/core` — affected >=0 <5.10.3

## Details
## Summary

Strapi's password hashing implementation using bcryptjs lacks maximum password length validation. Since bcryptjs truncates passwords exceeding 72 bytes, this creates potential vulnerabilities such as authentication bypass and performance degradation.

## POC
Create an admin user with a password exceeding 72 characters like 85,
Log in using only the first 72 characters of the password.
Authentication is successful, confirming the issue.

Proposed Solution Based on  discussions:

Add a maximum password length validation (72 characters) during password creation and updates for both Admin and U&P users.
Truncate passwords exceeding 72 bytes on the server before passing them to bcryptjs during login.
Optionally, issue a warning to users with passwords longer than 72 bytes during login, informing them of truncation.

## Impact
This issue affects all Strapi installations using bcryptjs for password hashing. Until resolved, it can lead to:
Authentication Bypass: Users may unknowingly set passwords exceeding 72 bytes, leading to truncated, predictable hashes.
Performance Issues: Excessively long passwords can degrade server performance.

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-2cjv-6wg9-f4f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-25298
- https://github.com/strapi/strapi/commit/41f8cdf116f7f464dae7d591e52d88f7bfa4b7cb
- https://github.com/strapi/strapi
