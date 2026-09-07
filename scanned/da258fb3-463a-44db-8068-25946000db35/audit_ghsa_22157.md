# [M] Jenkins Crowd Integration Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-r5jr-82x4-r6j7
CVE: CVE-2019-1003097
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r5jr-82x4-r6j7
Type: github-advisory

## Affected
- Maven: `com.ds.tools.hudson:crowd` — affected >=0

## Details
Jenkins Crowd Integration Plugin stores credentials unencrypted in the global config.xml configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003097
- https://github.com/jenkinsci/crowd-plugin
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1069
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
