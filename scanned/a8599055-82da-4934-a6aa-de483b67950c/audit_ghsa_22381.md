# [M] Stored cross-site scripting vulnerability in Jenkins TestLink Plugin

## Summary
Severity: Medium
Advisory: GHSA-3rrg-p8xc-3457
CVE: CVE-2018-1000113
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3rrg-p8xc-3457
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:testlink` — affected >=0 <2.13

## Details
A cross-site scripting vulnerability exists in Jenkins TestLink Plugin 2.12 and earlier in TestLinkBuildAction/summary.jelly and others that allow an attacker who can control e.g. TestLink report names to have Jenkins serve arbitrary HTML and JavaScript

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000113
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-731
