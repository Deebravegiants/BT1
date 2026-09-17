# [M] Maven Integration Plugin did not mask sensitive values in module build logs

## Summary
Severity: Medium
Advisory: GHSA-hr96-qfvm-52r6
CVE: CVE-2019-10358
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hr96-qfvm-52r6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:maven-plugin` — affected >=0 <3.4

## Details
Jenkins Maven Integration Plugin 3.3 and earlier did not apply build log decorators to module builds, potentially revealing sensitive build variables in the build log.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10358
- https://github.com/jenkinsci/maven-plugin/commit/23e3fe5c43705883e4fb9d3ba052dfb1af3f2464
- https://github.com/jenkinsci/maven-plugin
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-713
- http://www.openwall.com/lists/oss-security/2019/07/31/1
