# [M] Jenkins Open STF Plugin stores credentials in plain text 

## Summary
Severity: Medium
Advisory: GHSA-g2rp-qwrq-qqqq
CVE: CVE-2019-1003094
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g2rp-qwrq-qqqq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:open-stf` — affected >=0

## Details
Jenkins Open STF Plugin stores credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003094
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1059
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
