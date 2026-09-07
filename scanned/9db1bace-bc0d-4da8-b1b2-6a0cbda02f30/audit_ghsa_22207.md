# [M] Jenkins Slack Notification Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-22xp-7rcx-xp34
CVE: CVE-2019-1003043
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-22xp-7rcx-xp34
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:slack` — affected >=0 <2.20

## Details
Jenkins Slack Notification Plugin did not perform permission checks on a method implementing form validation. This allowed users with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, this form validation method did not require POST requests, resulting in a cross-site request forgery vulnerability.

This form validation method now requires POST requests and Overall/Administer (for global configuration) or Item/Configure permissions (for job configuration).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003043
- https://github.com/jenkinsci/slack-plugin/commit/0268bbefdcc283effd27be5318770f7e75c6f102
- https://github.com/jenkinsci/slack-plugin
- https://jenkins.io/security/advisory/2019-03-25/#SECURITY-976
- https://web.archive.org/web/20200227082607/http://www.securityfocus.com/bid/107628
- http://www.openwall.com/lists/oss-security/2019/03/28/2
