# [M] Persistent XSS vulnerability in Static Analysis Utilities

## Summary
Severity: Medium
Advisory: GHSA-9c2p-99pg-c4j9
CVE: CVE-2017-1000102
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9c2p-99pg-c4j9
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:analysis-core` — affected >=0 <1.92

## Details
The Details view of some Static Analysis Utilities based plugins, was vulnerable to a persisted cross-site scripting vulnerability: Malicious users able to influence the input to these plugins, for example the console output which is parsed to extract build warnings (Warnings Plugin), could insert arbitrary HTML into this view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000102
- https://jenkins.io/security/advisory/2017-08-07
- http://www.securityfocus.com/bid/101061
