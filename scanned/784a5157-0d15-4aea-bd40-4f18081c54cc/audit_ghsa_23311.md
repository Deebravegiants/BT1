# [H] Jenkins NeoLoad Plugin stores credentials in cleartext

## Summary
Severity: High
Advisory: GHSA-98p6-6428-77v7
CVE: CVE-2019-10440
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-98p6-6428-77v7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:neoload-jenkins-plugin` — affected >=0 <2.2.6

## Details
Jenkins NeoLoad Plugin prior to version 2.2.6 stores credentials unencrypted in its global configuration file and in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10440
- https://github.com/jenkinsci/neoload-plugin/commit/83c8300c8318502b4f4d4c802dd2a10cadfee4c9
- https://github.com/jenkinsci/neoload-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1427
- https://www.zerodayinitiative.com/advisories/ZDI-19-932
- http://www.openwall.com/lists/oss-security/2019/10/16/6
