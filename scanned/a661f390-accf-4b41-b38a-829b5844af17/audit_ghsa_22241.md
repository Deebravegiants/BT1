# [M] Password stored in plain text by Applatix Plugin

## Summary
Severity: Medium
Advisory: GHSA-54m9-h7qp-fwvg
CVE: CVE-2020-2133
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-54m9-h7qp-fwvg
Type: github-advisory

## Affected
- Maven: `com.applatix.jenkins:applatix` — affected >=0

## Details
Jenkins Applatix Plugin 1.1 and earlier stores a password unencrypted in job config.xml files on the Jenkins master where it can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2133
- https://github.com/jenkinsci/applatix-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1540
- http://www.openwall.com/lists/oss-security/2020/02/12/3
