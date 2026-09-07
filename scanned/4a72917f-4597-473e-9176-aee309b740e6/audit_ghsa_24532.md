# [M] Reflected XSS in Jenkins Compatibility Action Storage Plugin

## Summary
Severity: Medium
Advisory: GHSA-rfrq-3v89-fqg6
CVE: CVE-2020-2217
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rfrq-3v89-fqg6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:compatibility-action-storage` — affected >=0

## Details
Jenkins Compatibility Action Storage Plugin 1.0 and earlier does not escape the content coming from the MongoDB in the testConnection form validation endpoint, resulting in a reflected cross-site scripting (XSS) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2217
- https://github.com/jenkinsci/compatibility-action-storage-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1771
- http://www.openwall.com/lists/oss-security/2020/07/02/7
