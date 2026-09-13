# [H] Jenkins Plot Plugin XML External Entity Reference vulnerability

## Summary
Severity: High
Advisory: GHSA-wgpp-g6v9-7hxp
CVE: CVE-2022-46682
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-wgpp-g6v9-7hxp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:plot` — affected >=0 <2.1.12

## Details
Jenkins Plot Plugin 2.1.11 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control XML input files for the 'Plot build data' build step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Plot Plugin 2.1.12 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46682
- https://github.com/jenkinsci/plot-plugin/commit/4f7afbe064aab538a242a9984e583e513863e0ac
- https://github.com/jenkinsci/plot-plugin
- https://www.jenkins.io/security/advisory/2022-12-07/#SECURITY-2940
