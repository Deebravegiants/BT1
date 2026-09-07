# [M] Subversion Plugin stored XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x3pr-fcgm-wjgc
CVE: CVE-2020-2111
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x3pr-fcgm-wjgc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:subversion` — affected >=0 <2.13.1

## Details
Jenkins Subversion Plugin 2.13.0 and earlier does not escape the error message for the Project Repository Base URL field form validation, resulting in a stored cross-site scripting vulnerability. Subversion Plugin 2.13.1 escapes the affected part of the error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2111
- https://github.com/jenkinsci/subversion-plugin/commit/545ca52f6de9af7541621bbea716ead449cd2b98
- https://github.com/jenkinsci/subversion-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1725
- http://www.openwall.com/lists/oss-security/2020/02/12/3
