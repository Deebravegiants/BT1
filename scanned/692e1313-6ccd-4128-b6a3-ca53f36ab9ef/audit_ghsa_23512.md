# [M] CSRF vulnerability in Jenkins Shared Objects Plugin

## Summary
Severity: Medium
Advisory: GHSA-2v9x-gpq4-8gg2
CVE: CVE-2020-2296
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2v9x-gpq4-8gg2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:shared-objects` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Shared Objects Plugin 0.44 and earlier allows attackers to configure shared objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2296
- https://github.com/jenkinsci/shared-objects-plugin
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-2052
- http://www.openwall.com/lists/oss-security/2020/10/08/5
