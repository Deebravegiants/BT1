# [M] Cross-Site Request Forgery in Jenkins EasyQA Plugin

## Summary
Severity: Medium
Advisory: GHSA-g67p-jvvc-qf54
CVE: CVE-2022-34203
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-g67p-jvvc-qf54
Type: github-advisory

## Affected
- Maven: `com.geteasyqa:easyqa` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins EasyQA Plugin 1.0 and earlier allows attackers to connect to an attacker-specified HTTP server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34203
- https://github.com/jenkinsci/easyqa-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2281
