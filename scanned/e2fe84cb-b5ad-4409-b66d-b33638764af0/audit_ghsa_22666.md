# [M] Jenkins iceScrum Plugin vulnerable to Missing Authorization

## Summary
Severity: Medium
Advisory: GHSA-h5cx-w235-58hm
CVE: CVE-2019-10442
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h5cx-w235-58hm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:icescrum` — affected >=0 <1.1.6

## Details
A missing permission check in Jenkins iceScrum Plugin prior to version 1.1.6 allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials. This issue is patched in version 1.1.6

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10442
- https://github.com/jenkinsci/icescrum-plugin/commit/2e248f7e2cfc5deb2d796f9fbaf42d8ea33ccad4
- https://github.com/jenkinsci/icescrum-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1484
- http://www.openwall.com/lists/oss-security/2019/10/16/6
