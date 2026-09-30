# [H] Spring Security vulnerable to Authorization Bypass

## Summary
Severity: High
Advisory: GHSA-27xw-p8v6-9jjr
CVE: CVE-2018-15801
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-27xw-p8v6-9jjr
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=5.1.0 <5.1.2
- Maven: `org.springframework.security:spring-security-oauth2-jose` — affected >=5.1.0 <5.1.2

## Details
Spring Security versions 5.1.x prior to 5.1.2 contain an authorization bypass vulnerability during JWT issuer validation. In order to be impacted, the same private key for an honest issuer and a malicious user must be used when signing JWTs. In that case, a malicious user could fashion signed JWTs with the malicious issuer URL that may be granted for the honest issuer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15801
- https://github.com/spring-projects/spring-security/commit/c70b65c5df0e170a2d34d812b83db0b7bc71ea25
- https://github.com/advisories/GHSA-27xw-p8v6-9jjr
- https://github.com/spring-projects/spring-security
- https://pivotal.io/security/cve-2018-15801
