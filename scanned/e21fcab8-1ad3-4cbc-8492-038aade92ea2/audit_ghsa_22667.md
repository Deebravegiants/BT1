# [M] Server-Side Request Forgery (SSRF) in Jenkins Confluence Publisher Plugin

## Summary
Severity: Medium
Advisory: GHSA-5339-9974-hqj9
CVE: CVE-2018-1999039
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5339-9974-hqj9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:confluence-publisher` — affected >=0 <2.0.2

## Details
A server-side request forgery vulnerability exists in Jenkins Confluence Publisher Plugin 2.0.1 and earlier in ConfluenceSite.java that allows attackers to have Jenkins submit login requests to an attacker-specified Confluence server URL with attacker specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999039
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-982
