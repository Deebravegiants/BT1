# [M] Jenkins Pipeline Aggregator View Plugin stored XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jf8x-943c-r4h6
CVE: CVE-2019-16564
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jf8x-943c-r4h6
Type: github-advisory

## Affected
- Maven: `com.paul8620.jenkins.plugins:pipeline-aggregator-view` — affected >=0 <1.9

## Details
Jenkins Pipeline Aggregator View Plugin 1.8 and earlier does not escape information shown on its view, resulting in a stored XSS vulnerability exploitable by attackers able to affects view content such as job display name or pipeline stage names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16564
- https://github.com/jenkinsci/pipeline-aggregator-view-plugin/commit/acb0eeeae60ec0ac2dc5c8b5639d77589aa95af3
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1593
- http://www.openwall.com/lists/oss-security/2019/12/17/1
