# [M] Cross-Site Request Forgery in Jenkins XPath Configuration Viewer Plugin

## Summary
Severity: Medium
Advisory: GHSA-3q7f-w8fr-368v
CVE: CVE-2022-34812
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-3q7f-w8fr-368v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:xpath-config-viewer` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins XPath Configuration Viewer Plugin 1.1.1 and earlier allows attackers to create and delete XPath expressions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34812
- https://github.com/jenkinsci/xpath-config-viewer-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2658
