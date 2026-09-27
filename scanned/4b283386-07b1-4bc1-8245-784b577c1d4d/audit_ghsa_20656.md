# [M] Improper masking of credentials Jenkins in Git Plugin

## Summary
Severity: Medium
Advisory: GHSA-jxmw-3gxf-fprh
CVE: CVE-2022-38663
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-08-24
Source: https://github.com/advisories/GHSA-jxmw-3gxf-fprh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git` — affected >=0 <4.11.5

## Details
Jenkins Git Plugin 4.11.4 and earlier does not properly mask (i.e., replace with asterisks) credentials in the build log provided by the Git Username and Password (`gitUsernamePassword`) credentials binding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38663
- https://github.com/jenkinsci/git-plugin/commit/3241db9cc696711c871d4e78b3c3c0daad0740c3
- https://github.com/jenkinsci/git-plugin
- https://www.jenkins.io/security/advisory/2022-08-23/#SECURITY-2796
- http://www.openwall.com/lists/oss-security/2022/08/23/2
