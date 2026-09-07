# [M] Stored XSS vulnerability in Jenkins Static Analysis Utilities Plugin

## Summary
Severity: Medium
Advisory: GHSA-fg6g-52rg-vr9q
CVE: CVE-2020-2316
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fg6g-52rg-vr9q
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:analysis-core` — affected >=0

## Details
Jenkins Static Analysis Utilities Plugin 1.96 and earlier does not escape the annotation message in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2316
- https://github.com/jenkinsci/analysis-core-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-1907
