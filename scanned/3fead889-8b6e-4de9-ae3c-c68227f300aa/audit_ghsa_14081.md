# [M] Jenkins Email Extension Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2f89-66v2-9p53
CVE: CVE-2023-32980
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-2f89-66v2-9p53
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <2.96.1

## Details
Jenkins Email Extension Plugin 2.96 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This allows attackers to make another user stop watching an attacker-specified job.

Email Extension Plugin 2.96.1 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32980
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3088%20(2)
