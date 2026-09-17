# [H] Go Fiber CSRF Token Validation Vulnerability

## Summary
Severity: High
Advisory: GHSA-mv73-f69x-444p
CVE: CVE-2023-45141
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-mv73-f69x-444p
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.50.0

## Details
A Cross-Site Request Forgery (CSRF) vulnerability has been identified in the application, which allows an attacker to obtain tokens and forge malicious requests on behalf of a user. This can lead to unauthorized actions being taken on the user's behalf, potentially compromising the security and integrity of the application.

## Vulnerability Details

The vulnerability is caused by improper validation and enforcement of CSRF tokens within the application. The following issues were identified:

1. **Lack of Token Association**: The CSRF token was validated against tokens in storage but was not tied to the original requestor that generated it, allowing for token reuse.

## Remediation

To remediate this vulnerability, it is recommended to take the following actions:

1. **Update the Application**: Upgrade the application to a fixed version with a patch for the vulnerability.

2. **Implement Proper CSRF Protection**: Review the updated documentation and ensure your application's CSRF protection mechanisms follow best practices.

4. **Choose CSRF Protection Method**: Select the appropriate CSRF protection method based on your application's requirements, either the Double Submit Cookie method or the Synchronizer Token Pattern using sessions.

5. **Security Testing**: Conduct a thorough security assessment, including penetration testing, to identify and address any other security vulnerabilities.

## Defence-in-depth

Users should take additional security measures like captchas or Two-Factor Authentication (2FA) and set Session cookies with SameSite=Lax or SameSite=Strict, and the Secure and HttpOnly attributes.

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-mv73-f69x-444p
- https://nvd.nist.gov/vuln/detail/CVE-2023-45141
- https://github.com/gofiber/fiber/commit/8c3916dbf4ad2ed427d02c6eb63ae8b2fa8f019a
- https://github.com/gofiber/fiber/commit/b50d91d58ecdff2a330bf07950244b6c4caf65b1
- https://github.com/gofiber/fiber
