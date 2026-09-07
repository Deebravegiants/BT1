# [H] Session fixation vulnerability in Jenkins OpenId Connect Authentication Plugin

## Summary
Severity: High
Advisory: GHSA-h23j-73ww-7594
CVE: CVE-2024-52553
CWE: CWE-384, CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-h23j-73ww-7594
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:oic-auth` — affected >=0 <4.421.v5422614eb

## Details
Jenkins OpenId Connect Authentication Plugin 4.418.vccc7061f5b_6d and earlier does not invalidate the previous session on login. This allows attackers to use social engineering techniques to gain administrator access to Jenkins. OpenId Connect Authentication Plugin 4.421.v5422614eb_e0a_ invalidates the existing session on login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52553
- https://github.com/jenkinsci/oic-auth-plugin
- https://www.jenkins.io/security/advisory/2024-11-13/#SECURITY-3473
