# [H] XXE vulnerability in Jenkins WebSphere Deployer Plugin

## Summary
Severity: High
Advisory: GHSA-f5wx-w2f9-82gh
CVE: CVE-2020-2108
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f5wx-w2f9-82gh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:websphere-deployer` — affected >=0

## Details
WebSphere Deployer Plugin 1.6.1 and earlier does not configure the XML parser to prevent XML external entity (XXE) attacks. This could be exploited by a user with Job/Configure permissions to upload a specially crafted war file containing a `WEB-INF/ibm-web-ext.xml` which is parsed by the plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2108
- https://github.com/jenkinsci/websphere-deployer-plugin
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1719
- http://www.openwall.com/lists/oss-security/2020/01/29/1
