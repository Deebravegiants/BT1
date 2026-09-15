# [M] Improper Certificate Validation in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-fq9f-9wv9-rfmg
CVE: CVE-2017-1000396
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-fq9f-9wv9-rfmg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.73.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.74 <2.84

## Details
Jenkins 2.73.1 and earlier, 2.83 and earlier bundled a version of the commons-httpclient library with the vulnerability CVE-2012-6153 that incorrectly verified SSL certificates, making it susceptible to man-in-the-middle attacks. This library is widely used as a transitive dependency in Jenkins plugins. The fix for CVE-2012-6153 was backported to the version of commons-httpclient that is bundled in core and made available to plugins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000396
- https://github.com/jenkinsci/jenkins/commit/fe77d1c3dbf91ddf2a9f8e5ed882611455ab00d0
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-10-11
