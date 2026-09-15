# [M] Jenkins HTML Publisher Plugin Path traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-478x-m3mx-7j3f
CVE: CVE-2024-28151
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-478x-m3mx-7j3f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:htmlpublisher` — affected >=0 <1.32.1

## Details
Jenkins HTML Publisher Plugin 1.32 and earlier archives invalid symbolic links in report directories on agents and recreates them on the controller, allowing attackers with Item/Configure permission to determine whether a path on the Jenkins controller file system exists, without being able to access it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28151
- https://github.com/jenkinsci/htmlpublisher-plugin/commit/6b840248dd0d691bbac9b515cd750b3f925909b2
- https://github.com/jenkinsci/htmlpublisher-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3303
- http://www.openwall.com/lists/oss-security/2024/03/06/3
