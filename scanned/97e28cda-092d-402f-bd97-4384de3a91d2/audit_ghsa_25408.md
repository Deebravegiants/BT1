# [H] Broken Authentication in Atlassian Connect Express

## Summary
Severity: High
Advisory: GHSA-4v96-m8xv-x83v
CVE: CVE-2021-26073
CWE: CWE-287, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4v96-m8xv-x83v
Type: github-advisory

## Affected
- npm: `atlassian-connect-express` — affected >=3.0.2 <6.6.0

## Details
Broken Authentication in Atlassian Connect Express (ACE) from version 3.0.2 before version 6.6.0: Atlassian Connect Express is a Node.js package for building Atlassian Connect apps. Authentication between Atlassian products and the Atlassian Connect Express app occurs with a server-to-server JWT or a context JWT. Atlassian Connect Express versions between 3.0.2 - 6.5.0 erroneously accept context JWTs in lifecycle endpoints (such as installation) where only server-to-server JWTs should be accepted, permitting an attacker to send authenticated re-installation events to an app.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26073
- https://community.developer.atlassian.com/t/action-required-atlassian-connect-vulnerability-a%5B%E2%80%A6%5Dypass-of-app-qsh-verification-via-context-jwts/47072
- https://confluence.atlassian.com/pages/viewpage.action?pageId=1051986099
- https://security.netapp.com/advisory/ntap-20210604-0004
- http://bitbucket.org/atlassian/atlassian-connect-express
