# [M] Passwords stored in plain text by ElasTest Plugin

## Summary
Severity: Medium
Advisory: GHSA-p9rc-x48f-582x
CVE: CVE-2020-2274
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p9rc-x48f-582x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:elastest` — affected >=0

## Details
Jenkins ElasTest Plugin 1.2.1 and earlier stores its server password unencrypted in its global configuration file on the Jenkins controller where it can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2274
- https://github.com/jenkinsci/elastest-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-2014
- http://www.openwall.com/lists/oss-security/2020/09/16/3
