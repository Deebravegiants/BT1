# [H] Jenkins Sumologic Publisher Plugin vulnerable to cross-site request forgery

## Summary
Severity: High
Advisory: GHSA-7jrr-fwhw-762v
CVE: CVE-2023-37958
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-7jrr-fwhw-762v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sumologic-publisher` — affected >=0

## Details
Jenkins Sumologic Publisher Plugin 2.2.1 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37958
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3117
- http://www.openwall.com/lists/oss-security/2023/07/12/2
