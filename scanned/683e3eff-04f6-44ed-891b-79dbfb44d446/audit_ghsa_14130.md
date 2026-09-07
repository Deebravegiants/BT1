# [M] Jenkins AppSpider Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vgfw-766v-7q82
CVE: CVE-2023-32998
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-vgfw-766v-7q82
Type: github-advisory

## Affected
- Maven: `com.rapid7:jenkinsci-appspider-plugin` — affected >=0 <1.0.16

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins AppSpider Plugin 1.0.15 and earlier allows attackers to connect to an attacker-specified URL and send an HTTP POST request with a JSON payload consisting of attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32998
- https://github.com/jenkinsci/appspider-build-scanner-plugin
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3121
