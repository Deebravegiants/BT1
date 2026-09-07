# [M] CSRF vulnerability in Jenkins CVS Plugin

## Summary
Severity: Medium
Advisory: GHSA-63mw-hp3h-gc77
CVE: CVE-2020-2184
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-63mw-hp3h-gc77
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cvs` — affected >=0 <2.16

## Details
CVS Plugin 2.15 and earlier does not require POST requests in several HTTP endpoints, resulting in cross-site request forgery (CSRF) vulnerabilities. This allows attackers to create and manipulate tags, and to connect to an attacker-specified URL.

CVS Plugin 2.16 now requires POST requests for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2184
- https://github.com/jenkinsci/cvs-plugin/commit/8954b3a1e498f11c09296d4f54dc2de6a371c448
- https://github.com/jenkinsci/cvs-plugin
- https://jenkins.io/security/advisory/2020-05-06/#SECURITY-1094
- http://www.openwall.com/lists/oss-security/2020/05/06/3
