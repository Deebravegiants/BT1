# [M] Jenkins Wall Display Plugin Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hc34-f55m-rh3m
CVE: CVE-2019-10376
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hc34-f55m-rh3m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jenkinswalldisplay` — affected >=0

## Details
Wall Display Master Project Plugin does not properly escape the `customTheme` query parameter, resulting in a reflected cross-site scripting vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10376
- https://github.com/jenkinsci/walldisplay-plugin
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-751
- http://www.openwall.com/lists/oss-security/2019/08/07/1
