# [M] Broken Authentication in Atlassian Connect Spring Boot

## Summary
Severity: Medium
Advisory: GHSA-cpcr-74q9-74gp
CVE: CVE-2021-26074
CWE: CWE-287, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-cpcr-74q9-74gp
Type: github-advisory

## Affected
- Maven: `com.atlassian.connect:atlassian-connect-spring-boot-starter` — affected >=1.1.0 <2.1.3

## Details
Broken Authentication in Atlassian Connect Spring Boot (ACSB) from version 1.1.0 before version 2.1.3. Atlassian Connect Spring Boot is a Java Spring Boot package for building Atlassian Connect apps. Authentication between Atlassian products and the Atlassian Connect Spring Boot app occurs with a server-to-server JWT or a context JWT. Atlassian Connect Spring Boot versions between 1.1.0 - 2.1.2 erroneously accept context JWTs in lifecycle endpoints (such as installation) where only server-to-server JWTs should be accepted, permitting an attacker to send authenticated re-installation events to an app.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26074
- https://community.developer.atlassian.com/t/action-required-atlassian-connect-vulnerability-allows-bypass-of-app-qsh-verification-via-context-jwts/47072
- https://confluence.atlassian.com/pages/viewpage.action?pageId=1051986106
