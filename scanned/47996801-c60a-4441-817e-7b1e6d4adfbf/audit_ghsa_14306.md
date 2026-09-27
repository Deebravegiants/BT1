# [M] Spring Session session ID can be logged to the standard output stream

## Summary
Severity: Medium
Advisory: GHSA-r7qr-f43m-pxfr
CVE: CVE-2023-20866
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-13
Source: https://github.com/advisories/GHSA-r7qr-f43m-pxfr
Type: github-advisory

## Affected
- Maven: `org.springframework.session:spring-session-core` — affected >=3.0.0 <3.0.1

## Details
In Spring Session version 3.0.0, the session id can be logged to the standard output stream. This vulnerability exposes sensitive information to those who have access to the application logs and can be used for session hijacking. Specifically, an application is vulnerable if it is using HeaderHttpSessionIdResolver.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20866
- https://github.com/spring-projects/spring-session/issues/2215
- https://github.com/spring-projects/spring-session/commit/c98a7be0e2ced7f795018f05397dca4bd5ca8212
- https://github.com/spring-projects/spring-session
- https://spring.io/security/cve-2023-20866
