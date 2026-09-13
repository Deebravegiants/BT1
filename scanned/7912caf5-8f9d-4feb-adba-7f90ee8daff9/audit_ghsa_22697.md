# [M] Jenkins Oracle Cloud Infrastructure Compute Classic Plugin cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h668-p5hg-7mc5
CVE: CVE-2019-10456
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h668-p5hg-7mc5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oracle-cloud-infrastructure-compute-classic` — affected >=0

## Details
Jenkins Oracle Cloud Infrastructure Compute Classic Plugin does not perform permission checks on a method implementing form validation. This allows users with Overall/Read access to Jenkins to initiate a connection test to an attacker-specified server with attacker-specified username and password.

Additionally, the form validation method does not require POST requests, resulting in a CSRF vulnerability.

As of publication of this advisory there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10456
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1462
