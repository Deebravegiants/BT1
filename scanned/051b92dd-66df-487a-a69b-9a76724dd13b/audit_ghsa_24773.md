# [M] Password stored in plain text by Dynamic Extended Choice Parameter Plugin

## Summary
Severity: Medium
Advisory: GHSA-h6pp-v4j6-w76c
CVE: CVE-2020-2124
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h6pp-v4j6-w76c
Type: github-advisory

## Affected
- Maven: `com.moded.extendedchoiceparameter:dynamic_extended_choice_parameter` — affected >=0

## Details
Jenkins Dynamic Extended Choice Parameter Plugin 1.0.1 and earlier stores a password unencrypted in job config.xml files on the Jenkins master where it can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2124
- https://github.com/jenkinsci/dynamic-extended-choice-parameter-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1560
- http://www.openwall.com/lists/oss-security/2020/02/12/3
