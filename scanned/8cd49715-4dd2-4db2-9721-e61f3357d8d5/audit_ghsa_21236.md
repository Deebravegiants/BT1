# [H] Arbitrary file write vulnerability in Jenkins CLIF Performance Testing plugin

## Summary
Severity: High
Advisory: GHSA-6xf5-c3cx-67pv
CVE: CVE-2022-36894
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-6xf5-c3cx-67pv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:clif-performance-testing` — affected >=0 <71.v0741865e206f

## Details
An arbitrary file write vulnerability in Jenkins CLIF Performance Testing Plugin 64.vc0d66de1dfb_f and earlier allows attackers with Overall/Read permission to create or replace arbitrary files on the Jenkins controller file system with attacker-specified content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36894
- https://github.com/jenkinsci/clif-performance-testing-plugin/commit/0741865e206fdb2fe4cdbad7f9956de3121c7b26
- https://github.com/jenkinsci/clif-performance-testing-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2413
- http://www.openwall.com/lists/oss-security/2022/07/27/1
