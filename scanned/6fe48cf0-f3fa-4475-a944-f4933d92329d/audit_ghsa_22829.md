# [H] XXE vulnerability in Jenkins Valgrind Plugin

## Summary
Severity: High
Advisory: GHSA-xq2q-8hxc-7jr2
CVE: CVE-2020-2245
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xq2q-8hxc-7jr2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:valgrind` — affected >=0

## Details
Valgrind Plugin 0.28 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows a user able to control the input files for the Valgrind plugin parser to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2245
- https://github.com/jenkinsci/valgrind-plugin
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1829
- http://www.openwall.com/lists/oss-security/2020/09/01/3
