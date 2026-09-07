# [M] CSRF vulnerability in Jenkins Fortify on Demand Plugin

## Summary
Severity: Medium
Advisory: GHSA-p364-xfp2-f9rr
CVE: CVE-2020-2203
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p364-xfp2-f9rr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify-on-demand-uploader` — affected >=0 <6.0.0

## Details
A cross-site request forgery vulnerability in Jenkins Fortify on Demand Plugin 5.0.1 and earlier allows attackers to connect to the globally configured Fortify on Demand endpoint using attacker-specified credentials IDs.

This form validation method requires appropriate permission in Fortify on Demand Plugin 6.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2203
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin/commit/28932f7c5ff18f87d4b3a480225fb0827591776b
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1691
- http://www.openwall.com/lists/oss-security/2020/07/02/7
