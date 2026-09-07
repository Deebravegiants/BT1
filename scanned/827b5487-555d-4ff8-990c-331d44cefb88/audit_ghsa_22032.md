# [M] Relution Enterprise Appstore Publisher Jenkins Plugin contains Cross-Site Request Forgery 

## Summary
Severity: Medium
Advisory: GHSA-xjch-wqmw-fgcp
CVE: CVE-2019-10388
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xjch-wqmw-fgcp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:relution-publisher` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins Relution Enterprise Appstore Publisher Plugin 1.24 and earlier allows attackers to have Jenkins initiate an HTTP connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10388
- https://github.com/jenkinsci/relution-publisher-plugin
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1053
- http://www.openwall.com/lists/oss-security/2019/08/07/1
