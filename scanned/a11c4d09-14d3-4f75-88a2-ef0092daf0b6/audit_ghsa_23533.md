# [M] Secret stored in plain text by Jenkins GitHub Coverage Reporter Plugin

## Summary
Severity: Medium
Advisory: GHSA-5r5f-hcwf-r9jh
CVE: CVE-2020-2212
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5r5f-hcwf-r9jh
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:github-coverage-reporter` — affected >=0

## Details
GitHub Coverage Reporter Plugin 1.10 and earlier stores a GitHub access token in plain text in its global configuration file `io.jenkins.plugins.gcr.PluginConfiguration.xml`. This token can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2212
- https://github.com/jenkinsci/github-coverage-reporter-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1632
- http://www.openwall.com/lists/oss-security/2020/07/02/7
