# [M] Stored XSS vulnerability in Jenkins Artifact Repository Parameter Plugin

## Summary
Severity: Medium
Advisory: GHSA-gc87-qwmv-7x9x
CVE: CVE-2021-21622
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gc87-qwmv-7x9x
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:artifact-repository-parameter` — affected >=0 <1.0.1

## Details
Jenkins Artifact Repository Parameter Plugin 1.0.0 and earlier does not escape parameter names and descriptions.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

Jenkins Artifact Repository Parameter Plugin 1.0.1 escapes parameter names and descriptions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21622
- https://github.com/jenkinsci/artifact-repository-parameter-plugin/commit/84b63f7af101f68d7ccd5bc9c569f453f1f83f82
- https://github.com/jenkinsci/artifact-repository-parameter-plugin/commit/ac6659197807268b9947e80faeafffd35791f96f
- https://github.com/jenkinsci/artifact-repository-parameter-plugin
- https://www.jenkins.io/security/advisory/2021-02-24/#SECURITY-2168
