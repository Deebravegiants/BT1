# [M] Jenkins Beaker builder Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xfjq-5m4w-cc6h
CVE: CVE-2022-34208
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-xfjq-5m4w-cc6h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:beaker-builder` — affected >=0

## Details
Jenkins Beaker builder Plugin 1.10 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34208
- https://github.com/jenkinsci/beaker-builder-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2248
