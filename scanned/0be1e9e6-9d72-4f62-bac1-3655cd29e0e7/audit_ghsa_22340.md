# [H] Improper Authentication in Jenkins

## Summary
Severity: High
Advisory: GHSA-r57f-7xw3-q2r9
CVE: CVE-2017-1000354
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r57f-7xw3-q2r9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.50 <2.57
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.46.2

## Details
Jenkins versions 2.56 and earlier as well as 2.46.1 LTS and earlier are vulnerable to a login command which allowed impersonating any Jenkins user. The `login` command available in the remoting-based CLI stored the encrypted user name of the successfully authenticated user in a cache file used to authenticate further commands. Users with sufficient permission to create secrets in Jenkins, and download their encrypted values (e.g. with Job/Configure permission), were able to impersonate any other Jenkins user on the same instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000354
- https://github.com/jenkinsci/jenkins/commit/02d24053bdfeb219d2387a19885a60bdab510479
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-04-26
- https://web.archive.org/web/20200227174424/http://www.securityfocus.com/bid/98065
