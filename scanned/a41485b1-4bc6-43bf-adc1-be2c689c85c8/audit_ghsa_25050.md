# [M] Jenkins HipChat Plugin allows attackers with Overall/Read access to obtain credential IDs

## Summary
Severity: Medium
Advisory: GHSA-798p-53r7-mgw9
CVE: CVE-2018-1000419
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-798p-53r7-mgw9
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:hipchat` — affected >=0 <2.2.1

## Details
An improper authorization vulnerability exists in Jenkins HipChat Plugin 2.2.0 and earlier in HipChatNotifier.java that allows attackers with Overall/Read access to obtain credentials IDs for credentials stored in Jenkins. As of version 2.2.1, an enumeration of credentials IDs in this plugin requires Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000419
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-984%20(2)
- http://www.securityfocus.com/bid/106532
