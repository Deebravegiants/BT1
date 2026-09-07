# [M] Jenkins Warnings NG Plugin Cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wrr5-p265-7252
CVE: CVE-2019-10325
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wrr5-p265-7252
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=0 <5.1.0

## Details
A cross-site scripting vulnerability in Jenkins Warnings NG Plugin 5.0.0 and earlier allowed attacker with Job/Configure permission to inject arbitrary JavaScript in build overview pages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10325
- https://github.com/jenkinsci/warnings-ng-plugin/blob/main/CHANGELOG.md#510---2019-5-31
- https://jenkins.io/security/advisory/2019-05-31/#SECURITY-1373
- http://www.openwall.com/lists/oss-security/2019/05/31/2
- http://www.securityfocus.com/bid/108540
