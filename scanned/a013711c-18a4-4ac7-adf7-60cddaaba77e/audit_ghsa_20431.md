# [H] Agent-to-controller security bypass in Jenkins Debian Package Builder Plugin

## Summary
Severity: High
Advisory: GHSA-8xjp-rp29-v5j8
CVE: CVE-2022-23118
CWE: CWE-269, CWE-668, CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-8xjp-rp29-v5j8
Type: github-advisory

## Affected
- Maven: `ru.yandex.jenkins.plugins.debuilder:debian-package-builder` — affected >=0

## Details
Jenkins Debian Package Builder Plugin 1.6.11 and earlier implements functionality that allows agent processes to invoke command-line git at an attacker-specified path on the controller.

This allows attackers able to control agent processes to invoke arbitrary OS commands on the controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23118
- https://github.com/jenkinsci/debian-package-builder-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2546
- http://www.openwall.com/lists/oss-security/2022/01/12/6
