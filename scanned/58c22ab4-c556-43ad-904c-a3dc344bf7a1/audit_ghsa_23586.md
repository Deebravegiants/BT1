# [H] Stored XSS vulnerability in single axis builds tooltips in Jenkins Matrix Project Plugin

## Summary
Severity: High
Advisory: GHSA-h6qc-455m-7v6v
CVE: CVE-2020-2224
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h6qc-455m-7v6v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:matrix-project` — affected >=0 <1.17

## Details
Matrix Project Plugin 1.16 and earlier does not escape node names shown in tooltips on the overview page of builds with a single axis. This results in a stored cross-site scripting (XSS) vulnerability exploitable by users with Agent/Configure permission.

Matrix Project Plugin 1.17 escapes the node names shown in these tooltips.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2224
- https://github.com/jenkinsci/matrix-project-plugin/commit/b5f22a43147360896442c4a7719446a864898cb4
- https://github.com/jenkinsci/matrix-project-plugin
- https://jenkins.io/security/advisory/2020-07-15/#SECURITY-1924
- http://www.openwall.com/lists/oss-security/2020/07/15/5
