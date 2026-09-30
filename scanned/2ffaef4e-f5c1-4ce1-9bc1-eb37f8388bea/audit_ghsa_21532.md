# [H] Jenkins Config Rotator Plugin vulnerable to path traversal

## Summary
Severity: High
Advisory: GHSA-9pqq-h9qv-28fp
CVE: CVE-2022-45388
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-9pqq-h9qv-28fp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:config-rotator` — affected >=0

## Details
Jenkins Config Rotator Plugin 2.0.1 and earlier does not restrict a file name query parameter in an HTTP endpoint, allowing unauthenticated attackers to read arbitrary files with '.xml' extension on the Jenkins controller file system. Currently there is no known workaround and no fix available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45388
- https://github.com/jenkinsci/config-rotator-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2842
- http://www.openwall.com/lists/oss-security/2022/11/15/4
