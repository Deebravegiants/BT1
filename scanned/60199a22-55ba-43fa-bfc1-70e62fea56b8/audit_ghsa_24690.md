# [H] Jenkins HipChat Plugin allows credential capture due to incorrect authorization

## Summary
Severity: High
Advisory: GHSA-w3f7-2qfw-348x
CVE: CVE-2018-1000418
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w3f7-2qfw-348x
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:hipchat` — affected >=0 <2.2.1

## Details
An improper authorization vulnerability exists in Jenkins HipChat Plugin 2.2.0 and earlier in HipChatNotifier.java that allows attackers with Overall/Read access to send test notifications to an attacker-specified HipChat server with attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins. As of version 2.2.1, this form validation method requires POST requests and Overall/Administer permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000418
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-984%20(1)
- http://www.securityfocus.com/bid/106532
