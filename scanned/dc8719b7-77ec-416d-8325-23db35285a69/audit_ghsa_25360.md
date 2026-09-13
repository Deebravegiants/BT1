# [M] Improper permission checks in Jenkins Copy Artifact Plugin

## Summary
Severity: Medium
Advisory: GHSA-vv89-xggx-qqh2
CVE: CVE-2020-2183
CWE: CWE-276, CWE-285
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vv89-xggx-qqh2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:copyartifact` — affected >=0 <1.44

## Details
Copy Artifact Plugin 1.43.1 and earlier performs improper permission checks when determining whether a build can copy artifacts from another project build. This allows attackers, usually with Job/Configure permission, to configure jobs to copy artifacts from jobs they have no permission to access.

Copy Artifact Plugin 1.44 now properly performs permission checks when copying artifacts. When updating the plugin from a previous version, the previous behavior is retained (\"Migration mode\"). To enable the additional protections, switch to the new \"Production mode\". Doing so may cause existing jobs to fail to copy artifacts. For more information see the [plugin documentation](https://github.com/jenkinsci/copyartifact-plugin).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2183
- https://github.com/jenkinsci/copyartifact-plugin/commit/dc87de169604cb9b6706c5328e2e4aeb2c6652d6
- https://github.com/jenkinsci/copyartifact-plugin
- https://jenkins.io/security/advisory/2020-05-06/#SECURITY-988
- http://www.openwall.com/lists/oss-security/2020/05/06/3
