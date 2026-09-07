# [M] Open Redirect in Spring Security OAuth

## Summary
Severity: Medium
Advisory: GHSA-mmf6-6597-3v6m
CVE: CVE-2019-11269
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-mmf6-6597-3v6m
Type: github-advisory

## Affected
- Maven: `org.springframework.security.oauth:spring-security-oauth` — affected >=2.0.0.RELEASE <2.0.18.RELEASE
- Maven: `org.springframework.security.oauth:spring-security-oauth` — affected >=2.1.0.RELEASE <2.1.5.RELEASE
- Maven: `org.springframework.security.oauth:spring-security-oauth` — affected >=2.2.0.RELEASE <2.2.5.RELEASE
- Maven: `org.springframework.security.oauth:spring-security-oauth` — affected >=2.3.0.RELEASE <2.3.6.RELEASE

## Details
Spring Security OAuth versions 2.3 prior to 2.3.6, 2.2 prior to 2.2.5, 2.1 prior to 2.1.5, and 2.0 prior to 2.0.18, as well as older unsupported versions could be susceptible to an open redirector attack that can leak an authorization code. A malicious user or attacker can craft a request to the authorization endpoint using the authorization code grant type, and specify a manipulated redirection URI via the redirect_uri parameter. This can cause the authorization server to redirect the resource owner user-agent to a URI under the control of the attacker with the leaked authorization code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11269
- https://pivotal.io/security/cve-2019-11269
- https://www.oracle.com/security-alerts/cpujan2021.html
- http://packetstormsecurity.com/files/153299/Spring-Security-OAuth-2.3-Open-Redirection.html
