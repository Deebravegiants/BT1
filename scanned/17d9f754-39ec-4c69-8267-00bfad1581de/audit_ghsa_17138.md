# [M] Jenkins Delphix Plugin has improper SSL/TLS certificate validation

## Summary
Severity: Medium
Advisory: GHSA-pfh3-j79r-vqrj
CVE: CVE-2024-28162
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-pfh3-j79r-vqrj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:delphix` — affected >=3.0.1 <3.1.1

## Details
In Jenkins Delphix Plugin 3.0.1 through 3.1.0 (both inclusive) a global option for administrators to enable or disable SSL/TLS certificate validation for Data Control Tower (DCT) connections fails to take effect until Jenkins is restarted when switching from disabled validation to enabled validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28162
- https://github.com/jenkinsci/delphix-plugin/commit/798a36148526dbf6028eb6443f193c8f02c75cf2
- https://github.com/jenkinsci/delphix-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3330
- http://www.openwall.com/lists/oss-security/2024/03/06/3
