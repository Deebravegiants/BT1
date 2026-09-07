# [M] CSRF vulnerability in Jenkins Script Security Plugin

## Summary
Severity: Medium
Advisory: GHSA-qwgx-mrv5-87j8
CVE: CVE-2022-30946
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-qwgx-mrv5-87j8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1172.v35f6a

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Script Security Plugin 1158.v7c1b_73a_69a_08 and earlier allows attackers to have Jenkins send an HTTP request to an attacker-specified webserver.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30946
- https://github.com/jenkinsci/script-security-plugin/commit/35f6a0b8207ed3a32a85f27c1312da6cd738eeaa
- https://github.com/jenkinsci/script-security-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2116
- http://www.openwall.com/lists/oss-security/2022/05/17/8
