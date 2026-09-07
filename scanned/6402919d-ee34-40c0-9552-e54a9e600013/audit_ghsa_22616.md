# [M] Stored XSS vulnerability in Jenkins FindBugs Plugin

## Summary
Severity: Medium
Advisory: GHSA-24g8-35x9-fv8r
CVE: CVE-2020-2317
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-24g8-35x9-fv8r
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:findbugs` — affected >=0

## Details
Jenkins FindBugs Plugin 5.0.0 and earlier does not escape the annotation message in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to provide report files to Jenkins FindBugs Plugin's post build step.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2317
- https://github.com/jenkinsci/findbugs-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-1918
