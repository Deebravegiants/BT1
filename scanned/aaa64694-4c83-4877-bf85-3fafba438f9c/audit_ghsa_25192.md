# [M] Missing permission check in Jenkins Static Analysis Utilities Plugin

## Summary
Severity: Medium
Advisory: GHSA-vvfj-p4jf-j8rm
CVE: CVE-2019-10308
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vvfj-p4jf-j8rm
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:analysis-core` — affected >=0 <1.96

## Details
A missing permission check in Jenkins Static Analysis Utilities Plugin 1.95 and earlier in the DefaultGraphConfigurationView#doSave form handler method allowed attackers with Overall/Read permission to change the per-job default graph configuration for all users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10308
- https://github.com/jenkinsci/analysis-core-plugin/commit/3d7a0c7907d831c58541508b893dcea2039809c5
- https://github.com/jenkinsci/analysis-core-plugin
- https://jenkins.io/security/advisory/2019-04-30/#SECURITY-1100
- http://www.openwall.com/lists/oss-security/2019/04/30/5
- http://www.securityfocus.com/bid/108159
