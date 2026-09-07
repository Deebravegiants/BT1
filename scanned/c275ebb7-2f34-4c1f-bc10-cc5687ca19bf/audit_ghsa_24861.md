# [H] Stored XSS vulnerability in Coverage/Complexity Scatter Plot Plugin

## Summary
Severity: High
Advisory: GHSA-f6mg-hmfp-6grw
CVE: CVE-2020-2265
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f6mg-hmfp-6grw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:covcomplplot` — affected >=0

## Details
Jenkins Coverage/Complexity Scatter Plot Plugin 1.1.1 and earlier does not escape the method information in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to provide report files to the plugin's post-build step.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2265
- https://github.com/jenkinsci/covcomplplot-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1913
- http://www.openwall.com/lists/oss-security/2020/09/16/3
