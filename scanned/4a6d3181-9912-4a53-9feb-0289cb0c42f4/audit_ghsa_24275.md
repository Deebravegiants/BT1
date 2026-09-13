# [H] Jenkins iceScrum Plugin stores credentials in Cleartext

## Summary
Severity: High
Advisory: GHSA-362p-56c9-q273
CVE: CVE-2019-10443
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-362p-56c9-q273
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:icescrum` — affected >=0 <1.1.5

## Details
Jenkins iceScrum Plugin 1.1.4 and earlier stored credentials unencrypted in job config.xml files on the Jenkins master where they could be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10443
- https://github.com/jenkinsci/icescrum-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1436
- https://www.zerodayinitiative.com/advisories/ZDI-19-933
- http://www.openwall.com/lists/oss-security/2019/10/16/6
