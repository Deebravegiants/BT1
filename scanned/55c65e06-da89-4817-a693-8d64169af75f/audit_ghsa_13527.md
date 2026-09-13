# [C] CSRF Token Reuse Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-94w9-97p3-p368
CVE: CVE-2023-45128
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-94w9-97p3-p368
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.50.0

## Details
A Cross-Site Request Forgery (CSRF) vulnerability has been identified in the application, which allows an attacker to inject arbitrary values and forge malicious requests on behalf of a user. This vulnerability can allow an attacker to inject arbitrary values without any authentication, or perform various malicious actions on behalf of an authenticated user, potentially compromising the security and integrity of the application.

## Vulnerability Details

The vulnerability is caused by improper validation and enforcement of CSRF tokens within the application. The following issues were identified:

1. **Token Injection**: For 'safe' methods, the token was extracted from the cookie and saved to storage without further validation or sanitization.

2. **Lack of Token Association**: The CSRF token was validated against tokens in storage but not associated with a session, nor by using a Double Submit Cookie Method, allowing for token reuse.

### Specific Go Packages Affected
github.com/gofiber/fiber/v2/middleware/csrf

## Remediation

To remediate this vulnerability, it is recommended to take the following actions:

1. **Update the Application**: Upgrade the application to a fixed version with a patch for the vulnerability.

2. **Implement Proper CSRF Protection**: Review the updated documentation and ensure your application's CSRF protection mechanisms follow best practices.

4. **Choose CSRF Protection Method**: Select the appropriate CSRF protection method based on your application's requirements, either the Double Submit Cookie method or the Synchronizer Token Pattern using sessions.

5. **Security Testing**: Conduct a thorough security assessment, including penetration testing, to identify and address any other security vulnerabilities.

## Defence-in-depth

Users should take additional security measures like captchas or Two-Factor Authentication (2FA) and set Session cookies with SameSite=Lax or SameSite=Secure, and the Secure and HttpOnly attributes.

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-94w9-97p3-p368
- https://nvd.nist.gov/vuln/detail/CVE-2023-45128
- https://github.com/gofiber/fiber/commit/8c3916dbf4ad2ed427d02c6eb63ae8b2fa8f019a
- https://github.com/gofiber/fiber/commit/b50d91d58ecdff2a330bf07950244b6c4caf65b1
- https://github.com/gofiber/fiber
