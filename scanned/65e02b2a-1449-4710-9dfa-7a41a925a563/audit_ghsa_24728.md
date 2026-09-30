# [M] Jenkins Mattermost Notification Plugin vulnerable to SSRF

## Summary
Severity: Medium
Advisory: GHSA-wxj2-qc9p-65r3
CVE: CVE-2019-1003026
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wxj2-qc9p-65r3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mattermost` — affected >=0 <2.6.3

## Details
A server-side request forgery vulnerability exists in Jenkins Mattermost Notification Plugin 2.6.2 and earlier in MattermostNotifier.java that allows attackers with Overall/Read permission to have Jenkins connect to an attacker-specified Mattermost server and room and send a message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003026
- https://jenkins.io/security/advisory/2019-02-19/#SECURITY-985
- http://www.securityfocus.com/bid/107295
