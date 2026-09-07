# [M] CSRF vulnerability in Jenkins Active Directory Plugin

## Summary
Severity: Medium
Advisory: GHSA-2wf5-4mf7-vmh3
CVE: CVE-2020-2303
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2wf5-4mf7-vmh3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=0 <2.20

## Details
Jenkins Active Directory Plugin 2.19 and earlier does not require POST requests for multiple HTTP endpoints implementing connection and authentication tests, resulting in cross-site request forgery (CSRF) vulnerabilities.

This vulnerability allows attackers to perform connection tests, connecting to attacker-specified or previously configured Active Directory servers using attacker-specified credentials.

Active Directory Plugin 2.20 requires POST requests for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2303
- https://github.com/jenkinsci/active-directory-plugin/commit/3558971237b80e71e913ead9e82a722e9d5576b8
- https://github.com/jenkinsci/active-directory-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2126
- http://www.openwall.com/lists/oss-security/2020/11/04/6
