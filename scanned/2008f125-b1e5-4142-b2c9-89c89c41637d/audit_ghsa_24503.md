# [H] Jenkins Bitbucket OAuth Plugin contains Insufficiently Protected Credentials

## Summary
Severity: High
Advisory: GHSA-84h6-jf8x-ff2j
CVE: CVE-2019-10460
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-84h6-jf8x-ff2j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bitbucket-oauth` — affected >=0 <0.10

## Details
Jenkins Bitbucket OAuth Plugin prior to 0.10 stores credentials unencrypted in the global config.xml configuration file on the Jenkins master where they could be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10460
- https://github.com/jenkinsci/bitbucket-oauth-plugin/commit/f55d222db910220ca8cd8631fb746c98b9e12870
- https://github.com/jenkinsci/bitbucket-oauth-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1546
- http://www.openwall.com/lists/oss-security/2019/10/23/2
