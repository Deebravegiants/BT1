# [M] Jenkins Build Monitor View Plugin vulnerable to stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-5j5r-6mv9-m255
CVE: CVE-2024-28156
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-5j5r-6mv9-m255
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:build-monitor-plugin` — affected >=0

## Details
Jenkins Build Monitor View Plugin 1.14-860.vd06ef2568b_3f and earlier does not escape Build Monitor View names, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to configure Build Monitor Views.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28156
- https://github.com/jenkinsci/build-monitor-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3280
- http://www.openwall.com/lists/oss-security/2024/03/06/3
