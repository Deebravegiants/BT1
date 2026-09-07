# [M] CSRF vulnerability in Jenkins Keycloak Authentication Plugin 

## Summary
Severity: Medium
Advisory: GHSA-9wrr-4r9v-26xc
CVE: CVE-2023-24457
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-9wrr-4r9v-26xc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:keycloak` — affected >=0 <2.3.1

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Keycloak Authentication Plugin 2.3.0 and earlier allows attackers to trick users into logging in to the attacker's account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24457
- https://github.com/jenkinsci/keycloak-plugin/commit/e48da7b12473510092de6f74db29298171a30b7e
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2986
