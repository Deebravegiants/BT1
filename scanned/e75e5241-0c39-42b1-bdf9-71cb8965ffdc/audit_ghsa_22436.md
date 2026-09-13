# [H] Improper Input Validation in Jenkins

## Summary
Severity: High
Advisory: GHSA-wfj3-535m-p6fx
CVE: CVE-2017-1000391
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wfj3-535m-p6fx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.73.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.74 <2.89

## Details
Jenkins versions 2.88 and earlier and 2.73.2 and earlier stores metadata related to 'people', which encompasses actual user accounts, as well as users appearing in SCM, in directories corresponding to the user ID on disk. These directories used the user ID for their name without additional escaping, potentially resulting in problems like overwriting of unrelated configuration files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000391
- https://github.com/jenkinsci/jenkins/commit/566a8ddb885f0bef9bc848e60455c0aabbf0c1d3
- https://jenkins.io/security/advisory/2017-11-08
- http://www.securityfocus.com/bid/101773
