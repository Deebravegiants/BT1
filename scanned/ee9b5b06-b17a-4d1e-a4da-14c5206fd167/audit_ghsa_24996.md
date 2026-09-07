# [M] Missing permission check in Jenkins Implied Labels Plugin allows reconfiguring the plugin

## Summary
Severity: Medium
Advisory: GHSA-5hw2-327v-vvr6
CVE: CVE-2020-2282
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5hw2-327v-vvr6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:implied-labels` — affected >=0 <0.7

## Details
Implied Labels Plugin 0.6 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to configure the plugin.

Implied Labels Plugin 0.7 requires Overall/Administer permission to configure the plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2282
- https://github.com/jenkinsci/implied-labels-plugin/commit/9a5d38f8056a830ef075f379fa1b489c08f7000f
- https://github.com/jenkinsci/implied-labels-plugin
- https://www.jenkins.io/security/advisory/2020-09-23/#SECURITY-2004
- http://www.openwall.com/lists/oss-security/2020/09/23/1
