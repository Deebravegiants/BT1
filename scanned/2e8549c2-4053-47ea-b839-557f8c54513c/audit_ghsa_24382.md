# [M] Missing permission checks in Jenkins Maven Cascade Release Plugin

## Summary
Severity: Medium
Advisory: GHSA-5xv9-gp22-gqm5
CVE: CVE-2020-2294
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5xv9-gp22-gqm5
Type: github-advisory

## Affected
- Maven: `com.barchart.jenkins:maven-release-cascade` — affected >=0

## Details
Jenkins Maven Cascade Release Plugin 1.3.2 and earlier does not perform permission checks in several HTTP endpoints, allowing attackers with Overall/Read permission to start cascade builds and layout builds, and reconfigure the plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2294
- https://github.com/jenkinsci/maven-release-cascade-plugin
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-2049
- http://www.openwall.com/lists/oss-security/2020/10/08/5
