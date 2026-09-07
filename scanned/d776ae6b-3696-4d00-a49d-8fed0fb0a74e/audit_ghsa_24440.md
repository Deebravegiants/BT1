# [M] Reflected cross-site-scripting vulnerability in report URL of Jenkins CppNCSS Plugin

## Summary
Severity: Medium
Advisory: GHSA-xgmh-rvpw-6498
CVE: CVE-2018-1000108
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xgmh-rvpw-6498
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cppncss` — affected >=0 <1.2

## Details
A cross-site scripting vulnerability exists in Jenkins CppNCSS Plugin 1.1 and earlier in AbstractProjectAction/index.jelly that allow an attacker to craft links to Jenkins URLs that run arbitrary JavaScript in the user's browser when accessed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000108
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-712
