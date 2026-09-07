# [M] Cross-site Scripting in Jenkins Pipeline: Build Step Plugin

## Summary
Severity: Medium
Advisory: GHSA-9j65-3f2q-8q2r
CVE: CVE-2023-25762
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-9j65-3f2q-8q2r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-build-step` — affected >=0 <2.18.1

## Details
Jenkins Pipeline: Build Step Plugin 2.18 and earlier does not escape job names in a JavaScript expression used in the Pipeline Snippet Generator, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control job names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25762
- https://github.com/jenkinsci/pipeline-build-step-plugin/commit/0eaf88a695244ddb69d16c11b96659167dbead92
- https://github.com/jenkinsci/pipeline-build-step-plugin
- https://www.jenkins.io/security/advisory/2023-02-15/#SECURITY-3019
- http://www.openwall.com/lists/oss-security/2023/02/15/4
