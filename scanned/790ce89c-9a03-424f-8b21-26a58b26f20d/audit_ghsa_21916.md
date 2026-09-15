# [M] Path traversal vulnerability in Jenkins Fortify Plugin

## Summary
Severity: Medium
Advisory: GHSA-23h5-8ph6-7rfc
CVE: CVE-2022-25188
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-23h5-8ph6-7rfc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify` — affected >=0 <20.2.35

## Details
Jenkins Fortify Plugin 20.2.34 and earlier does not sanitize the `appName` and `appVersion` parameters of its Pipeline steps, which are used to write to files inside build directories.

This allows attackers with Item/Configure permission to write or overwrite `.xml` files on the Jenkins controller file system with content not controllable by the attacker.

Jenkins Fortify Plugin 20.2.35 sanitizes the `appName` and `appVersion` parameters of its Pipeline steps when determining the resulting filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25188
- https://github.com/jenkinsci/fortify-plugin/commit/ba3030cb63bb86b6bb13342664e0e319f2fee374
- https://github.com/jenkinsci/fortify-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2214
- http://www.openwall.com/lists/oss-security/2022/02/15/2
