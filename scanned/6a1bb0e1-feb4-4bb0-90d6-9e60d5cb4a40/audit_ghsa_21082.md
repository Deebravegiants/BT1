# [M] Jenkins XPath Configuration Viewer Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3fj7-78h2-w98x
CVE: CVE-2022-34813
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-3fj7-78h2-w98x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:xpath-config-viewer` — affected >=0

## Details
Jenkins XPath Configuration Viewer Plugin 1.1.1 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to create and delete XPath expressions.

Additionally, these HTTP endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34813
- https://github.com/jenkinsci/xpath-config-viewer-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2658
