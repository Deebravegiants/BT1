# [H] Jenkins Assembla Auth Plugin stores credentials in plain text 

## Summary
Severity: High
Advisory: GHSA-wmq3-24jm-m8xh
CVE: CVE-2019-10280
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wmq3-24jm-m8xh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:assembla-auth` — affected >=0 <1.13

## Details
Jenkins Assembla Auth Plugin stores credentials unencrypted in the global config.xml configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10280
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1093
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
