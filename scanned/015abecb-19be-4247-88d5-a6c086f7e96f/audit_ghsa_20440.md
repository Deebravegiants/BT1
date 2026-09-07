# [M] Stored XSS vulnerability in Jenkins Badge Plugin

## Summary
Severity: Medium
Advisory: GHSA-5qx5-vg5w-5mx3
CVE: CVE-2022-23108
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-5qx5-vg5w-5mx3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:badge` — affected >=0 <1.9.1

## Details
Jenkins Badge Plugin 1.9 and earlier does not escape the description and does not check for allowed protocols when creating a badge, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23108
- https://github.com/jenkinsci/badge-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2547
- http://www.openwall.com/lists/oss-security/2022/01/12/6
