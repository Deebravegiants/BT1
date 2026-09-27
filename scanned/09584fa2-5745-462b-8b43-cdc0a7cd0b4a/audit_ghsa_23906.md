# [M] Jenkins Crowd 2 Integration Plugin server-side request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-grmg-5q49-mqmf
CVE: CVE-2018-1000422
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-grmg-5q49-mqmf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:crowd2` — affected >=0 <2.0.1

## Details
An improper authorization vulnerability exists in Jenkins Crowd 2 Integration Plugin 2.0.0 and earlier in CrowdSecurityRealm.java that allows attackers to have Jenkins perform a connection test, connecting to an attacker-specified server with attacker-specified credentials and connection settings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000422
- https://github.com/jenkinsci/crowd2-plugin/commit/a93d0fa221454adb4087520d8c1c087828211598
- https://github.com/jenkinsci/crowd2-plugin
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1067
- https://web.archive.org/web/20200227092927/http://www.securityfocus.com/bid/106532
