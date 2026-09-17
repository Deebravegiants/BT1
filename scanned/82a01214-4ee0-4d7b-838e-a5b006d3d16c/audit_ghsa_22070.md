# [M] Jenkins Global Post Script Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-24w5-w6fw-qqx7
CVE: CVE-2019-10474
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-24w5-w6fw-qqx7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:global-post-script` — affected >=0

## Details
Jenkins Global Post Script Plugin does not perform permission checks on a method implementing form validation. This allows users with Overall/Read permission to list the files contained in `$JENKINS_HOME/global-post-script` that can be used by the plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10474
- https://github.com/jenkinsci/global-post-script-plugin/commit/6ef4d89279fe1b4c4f19f4622294893ba7f36040
- https://github.com/jenkinsci/global-post-script-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1073
- http://www.openwall.com/lists/oss-security/2019/10/23/2
