# [M] Password stored in plain text by Parasoft Environment Manager Plugin

## Summary
Severity: Medium
Advisory: GHSA-gmg2-3w6v-945p
CVE: CVE-2020-2132
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gmg2-3w6v-945p
Type: github-advisory

## Affected
- Maven: `com.parasoft:environment-manager` — affected >=0 <2.15

## Details
Jenkins Parasoft Environment Manager Plugin 2.14 and earlier stores a password unencrypted in job config.xml files on the Jenkins master where it can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2132
- https://github.com/jenkinsci/environment-manager-tools-plugin/commit/a2511b9d3dfbd3778471c6840ae6026076f11134
- https://github.com/jenkinsci/environment-manager-tools-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1562
- http://www.openwall.com/lists/oss-security/2020/02/12/3
