# [M] Stored XSS vulnerability in Jenkins Build With Parameters Plugin

## Summary
Severity: Medium
Advisory: GHSA-xjrg-6fv9-6rjg
CVE: CVE-2021-21628
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xjrg-6fv9-6rjg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:build-with-parameters` — affected >=0 <1.5.1

## Details
Jenkins Build With Parameters Plugin 1.5 and earlier does not escape parameter names and descriptions.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

Jenkins Build With Parameters Plugin 1.5.1 escapes parameter names and descriptions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21628
- https://github.com/jenkinsci/build-with-parameters-plugin/commit/edbc286cfd1419a40589a8c40d03ef9fe71dccf9
- https://github.com/jenkinsci/build-with-parameters-plugin
- https://www.jenkins.io/security/advisory/2021-03-30/#SECURITY-2231
- http://www.openwall.com/lists/oss-security/2021/03/30/1
