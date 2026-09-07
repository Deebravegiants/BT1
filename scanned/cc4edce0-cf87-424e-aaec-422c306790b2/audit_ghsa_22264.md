# [M] Jenkins iceScrum Plugin vulnerable to Cross-site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-rxvx-9wg5-qpww
CVE: CVE-2019-10441
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rxvx-9wg5-qpww
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:icescrum` — affected >=0 <1.1.6

## Details
A cross-site request forgery vulnerability in Jenkins iceScrum Plugin prior to version 1.1.6 allows attackers to connect to an attacker-specified URL using attacker-specified credentials. This issue is patched in version 1.1.6

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10441
- https://github.com/jenkinsci/icescrum-plugin/commit/2e248f7e2cfc5deb2d796f9fbaf42d8ea33ccad4
- https://github.com/jenkinsci/icescrum-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1484
