# [M] Jenkins CollabNet Plugin man in the middle vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m8x2-4gc8-9v3r
CVE: CVE-2018-1000605
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-m8x2-4gc8-9v3r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:collabnet` — affected >=0 <2.0.5

## Details
A man in the middle vulnerability exists in Jenkins CollabNet Plugin 2.0.4 and earlier in CollabNetApp.java, CollabNetPlugin.java, CNFormFieldValidator.java that allows attackers to impersonate any service that Jenkins connects to. CollabNet Plugin 2.0.5 and newer no longer does that. It instead requires users to opt in to disabling SSL/TLS certificate validation by setting the system property hudson.plugins.collabnet.CollabNetPlugin.skipSslValidation to true. This feature applies to connections by this plugin only.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000605
- https://github.com/jenkinsci/collabnet-plugin
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-941
