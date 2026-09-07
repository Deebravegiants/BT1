# [M] Path traversal vulnerability in Jenkins Matrix Project Plugin

## Summary
Severity: Medium
Advisory: GHSA-cjgm-9vc9-56mx
CVE: CVE-2024-23900
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-cjgm-9vc9-56mx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:matrix-project` — affected >=0 <822.824.v14451b

## Details
Jenkins Matrix Project Plugin 822.v01b_8c85d16d2 and earlier does not sanitize user-defined axis names of multi-configuration projects submitted through the `config.xml` REST API endpoint.

This allows attackers with Item/Configure permission to create or replace any `config.xml` file on the Jenkins controller file system with content not controllable by the attackers.

Matrix Project Plugin 822.824.v14451b_c0fd42 sanitizes user-defined axis names of Multi-configuration project.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23900
- https://github.com/jenkinsci/matrix-project-plugin/commit/f7a5b24905f69896234da34250171c1be80cddb4
- https://github.com/jenkinsci/matrix-project-plugin
- https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3289
- http://www.openwall.com/lists/oss-security/2024/01/24/6
