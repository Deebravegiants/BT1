# [H] Improper Authorization in Jenkins Core

## Summary
Severity: High
Advisory: GHSA-6rh5-23hx-j452
CVE: CVE-2019-1003003
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6rh5-23hx-j452
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.150.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.151 <2.159

## Details
An improper authorization vulnerability exists in Jenkins 2.158 and earlier, LTS 2.150.1 and earlier in core/src/main/java/hudson/security/TokenBasedRememberMeServices2.java that allows attackers with Overall/RunScripts permission to craft Remember Me cookies that would never expire, allowing e.g. to persist access to temporarily compromised user accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003003
- https://github.com/jenkinsci/jenkins/commit/7b4649657f90e98a5564cf5f0892deaa5fee0454
- https://access.redhat.com/errata/RHBA-2019:0327
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2019-01-16/#SECURITY-868
- https://web.archive.org/web/20200227092104/http://www.securityfocus.com/bid/106680
