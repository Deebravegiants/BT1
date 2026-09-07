# [M] Stored XSS vulnerability in Jenkins Git Changelog Plugin

## Summary
Severity: Medium
Advisory: GHSA-jcmg-9rw5-9rm2
CVE: CVE-2018-1000426
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jcmg-9rw5-9rm2
Type: github-advisory

## Affected
- Maven: `de.wellnerbou.jenkins:git-changelog` — affected >=0 <2.7

## Details
A cross-site scripting vulnerability exists in Jenkins Git Changelog Plugin 2.6 and earlier in GitChangelogSummaryDecorator/summary.jelly, GitChangelogLeftsideBuildDecorator/badge.jelly, GitLogJiraFilterPostPublisher/config.jelly, GitLogBasicChangelogPostPublisher/config.jelly that allows attackers able to control the Git history parsed by the plugin to have Jenkins render arbitrary HTML on some pages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000426
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1122
- http://www.securityfocus.com/bid/106532
