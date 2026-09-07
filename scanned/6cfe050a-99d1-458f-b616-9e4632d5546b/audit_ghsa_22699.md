# [H] Stored XSS vulnerability in ClearCase Release Plugin

## Summary
Severity: High
Advisory: GHSA-2c84-35rv-6q3f
CVE: CVE-2020-2270
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2c84-35rv-6q3f
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:clearcase-release` — affected >=0

## Details
Jenkins ClearCase Release Plugin 0.3 and earlier does not escape the composite baseline in badge tooltip, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2270
- https://github.com/jenkinsci/clearcase-release-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1911
- http://www.openwall.com/lists/oss-security/2020/09/16/3
