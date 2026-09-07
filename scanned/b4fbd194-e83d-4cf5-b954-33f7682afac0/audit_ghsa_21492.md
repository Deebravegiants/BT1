# [H] Jenkins Associated Files Plugin vulnerable to cross-site scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-chcg-gh9p-96c5
CVE: CVE-2022-45401
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-chcg-gh9p-96c5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:associated-files-plugin` — affected >=0

## Details
Jenkins Associated Files Plugin 0.2.1 and earlier does not escape names of associated files, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission. Currently, there are no known workarounds or patches.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45401
- https://github.com/jenkinsci/associated-files-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2947
- http://www.openwall.com/lists/oss-security/2022/11/15/4
