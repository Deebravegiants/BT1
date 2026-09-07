# [H] Authorization bypass in org.springframework.security.oauth:spring-security-oauth2

## Summary
Severity: High
Advisory: GHSA-h8w4-qv99-f7vj
CVE: CVE-2018-15758
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-h8w4-qv99-f7vj
Type: github-advisory

## Affected
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.0.0 <2.0.16
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.1.0 <2.1.3
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.2.0 <2.2.3.RELEASE
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.3.0 <2.3.4.RELEASE

## Details
Spring Security OAuth, versions 2.3 prior to 2.3.4, and 2.2 prior to 2.2.3, and 2.1 prior to 2.1.3, and 2.0 prior to 2.0.16, and older unsupported versions could be susceptible to a privilege escalation under certain conditions. A malicious user or attacker can craft a request to the approval endpoint that can modify the previously saved authorization request and lead to a privilege escalation on the subsequent approval. This scenario can happen if the application is configured to use a custom approval endpoint that declares AuthorizationRequest as a controller method argument. This vulnerability exposes applications that meet all of the following requirements: Act in the role of an Authorization Server (e.g. @EnableAuthorizationServer) and use a custom Approval Endpoint that declares AuthorizationRequest as a controller method argument. This vulnerability does not expose applications that: Act in the role of an Authorization Server and use the default Approval Endpoint, act in the role of a Resource Server only (e.g. @EnableResourceServer), act in the role of a Client only (e.g. @EnableOAuthClient).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15758
- https://github.com/spring-attic/spring-security-oauth/commit/4082ec7ae3d39198a47b5c803ccb20dacefb0b0
- https://github.com/spring-attic/spring-security-oauth/commit/623776689fdcc8047f5a908c71f348e1f172a97
- https://github.com/spring-attic/spring-security-oauth/commit/ddd65cd9417ae1e4a69e4193a622300db38e2ef
- https://github.com/spring-attic/spring-security-oauth/commit/f92223afc71687bd3156298054903f50aa71fbf
- https://access.redhat.com/errata/RHSA-2019:2413
- https://github.com/advisories/GHSA-h8w4-qv99-f7vj
- https://pivotal.io/security/cve-2018-15758
- http://www.securityfocus.com/bid/105687
