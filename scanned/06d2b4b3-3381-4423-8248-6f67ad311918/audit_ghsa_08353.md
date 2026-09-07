# [M] Jenkins buildgraph-view Plugin does not escape the build URL

## Summary
Severity: Medium
Advisory: GHSA-43ph-42gv-7965
CVE: CVE-2026-48927
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-43ph-42gv-7965
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:buildgraph-view` — affected >=0

## Details
Jenkins buildgraph-view Plugin 1.8 and earlier does not escape the build URL.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to configure jobs or views.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48927
- https://github.com/jenkinsci/buildgraph-view-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3486
