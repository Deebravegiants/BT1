# [H] RCE vulnerability in RadarGun Plugin

## Summary
Severity: High
Advisory: GHSA-723p-9rcj-xv8j
CVE: CVE-2020-2123
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-723p-9rcj-xv8j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:radargun` — affected >=0 <1.8

## Details
RadarGun Plugin 1.7 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution vulnerability exploitable by users able to configure RadarGun Plugin’s build step.

RadarGun Plugin 1.8 configures its YAML parser to only instantiate safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2123
- https://github.com/jenkinsci/radargun-plugin/commit/63aba3b31d1a8ea140f26923eb48a25ef7f87e87
- https://github.com/jenkinsci/radargun-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1733
- http://www.openwall.com/lists/oss-security/2020/02/12/3
