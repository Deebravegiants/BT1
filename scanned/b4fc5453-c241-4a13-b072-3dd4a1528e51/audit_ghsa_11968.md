# [C] pac4j-jwt: JwtAuthenticator Authentication Bypass via JWE-Wrapped PlainJWT

## Summary
Severity: Critical
Advisory: GHSA-pm7g-w2cf-q238
CVE: CVE-2026-29000
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-pm7g-w2cf-q238
Type: github-advisory

## Affected
- Maven: `org.pac4j:pac4j-jwt` — affected >=6.0.4.1 <6.3.3
- Maven: `org.pac4j:pac4j-jwt` — affected >=5.0.0-RC1 <5.7.9
- Maven: `org.pac4j:pac4j-jwt` — affected >=0 <4.5.9

## Details
pac4j-jwt versions prior to 4.5.9, 5.7.9, and 6.3.3 contain an authentication bypass vulnerability in JwtAuthenticator when processing encrypted JWTs that allows remote attackers to forge authentication tokens. Attackers who possess the server's RSA public key can create a JWE-wrapped PlainJWT with arbitrary subject and role claims, bypassing signature verification to authenticate as any user including administrators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-29000
- https://github.com/pac4j/pac4j
- https://www.codeant.ai/security-research/pac4j-jwt-authentication-bypass-public-key
- https://www.pac4j.org/blog/security-advisory-pac4j-jwt-jwtauthenticator.html
- https://www.vulncheck.com/advisories/pac4j-jwt-jwtauthenticator-authentication-bypass
