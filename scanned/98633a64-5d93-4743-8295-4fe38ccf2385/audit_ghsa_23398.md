# [M] Jenkins Perfecto Mobile Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-cq9m-rpm5-27m9
CVE: CVE-2019-1003095
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cq9m-rpm5-27m9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:perfectomobile` — affected >=0

## Details
Jenkins Perfecto Mobile Plugin stores credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003095
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1061
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
