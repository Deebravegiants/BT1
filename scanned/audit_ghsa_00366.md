# [C] Spring Security OAuth vulnerable to remote code execution (RCE)

## Summary
Severity: Critical
Advisory: GHSA-rrpm-pj7p-7j9q
CVE: CVE-2018-1260
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-rrpm-pj7p-7j9q
Type: github-advisory

## Affected
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.3.0 <2.3.3
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.2.0 <2.2.2
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.1.0 <2.1.2
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=2.0.0 <2.0.15
- Maven: `org.springframework.security.oauth:spring-security-oauth2` — affected >=1.0.0

## Details
Spring Security OAuth versions prior to 2.3.3, prior to 2.2.2, prior to 2.1.2, and prior to 2.0.15 contain a remote code execution vulnerability. An attacker can craft an authorization request to the authorization endpoint that can lead to remote code execution when the resource owner is forwarded to the approval endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1260
- https://access.redhat.com/errata/RHSA-2018:1809
- https://access.redhat.com/errata/RHSA-2018:2939
- https://github.com/advisories/GHSA-rrpm-pj7p-7j9q
- https://github.com/spring-attic/spring-security-oauth
- https://pivotal.io/security/cve-2018-1260
- https://web.archive.org/web/20200227123539/http://www.securityfocus.com/bid/104158
