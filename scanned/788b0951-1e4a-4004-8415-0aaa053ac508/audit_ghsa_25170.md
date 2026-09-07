# [M] Jenkins Maven Release Plugin contains Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r4rv-cq77-6p24
CVE: CVE-2019-10359
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r4rv-cq77-6p24
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.m2release:m2release` — affected >=0 <0.15.0

## Details
A cross-site request forgery vulnerability in Jenkins Maven Release Plugin prior to 0.15.0 in the M2ReleaseAction#doSubmit method allowed attackers to perform releases with attacker-specified options.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10359
- https://github.com/jenkinsci/m2release-plugin/commit/2f1117d011e1ef200f28bbb0c24bf918b89704b6
- https://github.com/jenkinsci/m2release-plugin
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1098
- http://www.openwall.com/lists/oss-security/2019/07/31/1
