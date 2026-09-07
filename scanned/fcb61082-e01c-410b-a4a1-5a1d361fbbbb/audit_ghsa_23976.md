# [H] Jenkins Delphix Plugin vulnerable to Cleartext credential storage

## Summary
Severity: High
Advisory: GHSA-4p59-p85x-f3wx
CVE: CVE-2019-10453
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4p59-p85x-f3wx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:delphix` — affected >=0

## Details
Jenkins Delphix Plugin stores credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10453
- https://github.com/jenkinsci/delphix-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1450
- http://www.openwall.com/lists/oss-security/2019/10/16/6
