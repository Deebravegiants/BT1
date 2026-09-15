# [M] Parse Server vulnerable to user enumeration via email verification endpoint

## Summary
Severity: Medium
Advisory: GHSA-w54v-hf9p-8856
CVE: CVE-2026-31901
CWE: CWE-204
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-w54v-hf9p-8856
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.6.0-alpha.8
- npm: `parse-server` — affected >=0 <8.6.34

## Details
### Impact

The email verification endpoint (`/verificationEmailRequest`) returns distinct error responses depending on whether an email address belongs to an existing user, is already verified, or does not exist. An attacker can send requests with different email addresses and observe the error codes to determine which email addresses are registered in the application.

This is a user enumeration vulnerability that affects any Parse Server deployment with email verification enabled (`verifyUserEmails: true`).

### Patches

The fix introduces a new Parse Server option `emailVerifySuccessOnInvalidEmail` (default: `true`) that returns a generic success response for all verification email requests, regardless of whether the email address is valid, already verified, or non-existent. This prevents an attacker from distinguishing between these cases.

The fix also strengthens the input validation for the related `resetPasswordSuccessOnInvalidEmail` option, and adds security checks that warn when either enumeration mitigation is disabled.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-w54v-hf9p-8856
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.8
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.34

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-w54v-hf9p-8856
- https://nvd.nist.gov/vuln/detail/CVE-2026-31901
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.34
- https://github.com/parse-community/parse-server/releases/tag/9.6.0-alpha.8
