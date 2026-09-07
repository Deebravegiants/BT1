# [M] Jenkins AppSpider Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-2c5c-fhr8-pwh9
CVE: CVE-2023-32999
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-2c5c-fhr8-pwh9
Type: github-advisory

## Affected
- Maven: `com.rapid7:jenkinsci-appspider-plugin` — affected >=0 <1.0.16

## Details
Jenkins AppSpider Plugin 1.0.15 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL and send an HTTP POST request with a JSON payload consisting of attacker-specified credentials.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

AppSpider Plugin 1.0.16 requires POST requests and Overall/Administer permission for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32999
- https://github.com/jenkinsci/appspider-build-scanner-plugin
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3121
