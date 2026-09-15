# [M] Jenkins build-metrics Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qv56-j8fg-39h6
CVE: CVE-2022-34785
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-qv56-j8fg-39h6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:build-metrics` — affected >=0

## Details
Jenkins build-metrics Plugin 1.3 and earlier does not perform a permission check in multiple HTTP endpoints.

This allows attackers with Overall/Read permission to obtain information about jobs otherwise inaccessible to them.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34785
- https://github.com/jenkinsci/build-metrics-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2643
