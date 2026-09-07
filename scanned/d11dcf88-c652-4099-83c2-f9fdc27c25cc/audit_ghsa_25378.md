# [M] CSRF vulnerability in Jenkins Maven Cascade Release Plugin

## Summary
Severity: Medium
Advisory: GHSA-wfpw-hqjg-58ph
CVE: CVE-2020-2295
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wfpw-hqjg-58ph
Type: github-advisory

## Affected
- Maven: `com.barchart.jenkins:maven-release-cascade` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Maven Cascade Release Plugin 1.3.2 and earlier allows attackers to start cascade builds and layout builds, and reconfigure the plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2295
- https://github.com/jenkinsci/maven-release-cascade-plugin
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-2049
- http://www.openwall.com/lists/oss-security/2020/10/08/5
