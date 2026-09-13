# [M] Jenkins secure flag not set on session cookies

## Summary
Severity: Medium
Advisory: GHSA-g7cf-wg27-qw87
CVE: CVE-2014-9634
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g7cf-wg27-qw87
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.586

## Details
Jenkins before 1.586 does not set the secure flag on session cookies when run on Tomcat 7.0.41 or later, which makes it easier for remote attackers to capture cookies by intercepting their transmission within an HTTP session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9634
- https://github.com/jenkinsci/jenkins/commit/582128b9ac179a788d43c1478be8a5224dc19710
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=769682
- https://bugzilla.redhat.com/show_bug.cgi?id=1185148
- https://issues.jenkins-ci.org/browse/JENKINS-25019
- https://jenkins.io/changelog-old
- http://www.openwall.com/lists/oss-security/2015/01/22/3
- http://www.securityfocus.com/bid/72054
