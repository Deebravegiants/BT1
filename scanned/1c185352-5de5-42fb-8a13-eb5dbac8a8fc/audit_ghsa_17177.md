# [H] Jenkins HTML Publisher Plugin does not properly sanitize input

## Summary
Severity: High
Advisory: GHSA-8vcg-v7g4-3vr7
CVE: CVE-2024-28149
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-8vcg-v7g4-3vr7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:htmlpublisher` — affected >=1.16 <1.32.1

## Details
Jenkins HTML Publisher Plugin 1.16 through 1.32 (both inclusive) does not properly sanitize input, allowing attackers with Item/Configure permission to implement cross-site scripting (XSS) attacks and to determine whether a path on the Jenkins controller file system exists.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28149
- https://github.com/jenkinsci/htmlpublisher-plugin/commit/8bf2e2297a86ad50f7567fb953b2f8ec18b2891b
- https://github.com/jenkinsci/htmlpublisher-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3301
- http://www.openwall.com/lists/oss-security/2024/03/06/3
