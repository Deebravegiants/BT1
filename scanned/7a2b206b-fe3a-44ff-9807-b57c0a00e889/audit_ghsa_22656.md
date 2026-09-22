# [M] Arbitrary file write vulnerability in Jenkins Storable Configs Plugin

## Summary
Severity: Medium
Advisory: GHSA-qv6q-4jwx-7j5c
CVE: CVE-2020-2278
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qv6q-4jwx-7j5c
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:storable-configs-plugin` — affected >=0

## Details
Jenkins Storable Configs Plugin 1.0 and earlier does not restrict the user-specified file name, allowing attackers with Job/Configure permission to replace any other '.xml' file on the Jenkins controller with a job config.xml file's content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2278
- https://github.com/jenkinsci/storable-configs-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1968%20(2)
- http://www.openwall.com/lists/oss-security/2020/09/16/3
