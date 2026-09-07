# [M] Jenkins Extra Columns Plugin allows Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-mr4j-7jjv-24m7
CVE: CVE-2016-3101
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mr4j-7jjv-24m7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:extra-columns` — affected >=0 <1.17

## Details
Cross-site scripting (XSS) vulnerability in the Extra Columns plugin before 1.17 in Jenkins allows remote attackers to inject arbitrary web script or HTML by leveraging failure to filter tool tips through the configured markup formatter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3101
- https://github.com/jenkinsci/extra-columns-plugin/commit/028ee0b324299271e7c244f8cb5cc9c4a87c72cf
- https://github.com/jenkinsci/extra-columns-plugin
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-04-11
