# [M] Persistent XSS vulnerability in Jenkins DRY Plugin

## Summary
Severity: Medium
Advisory: GHSA-63cj-3r94-234v
CVE: CVE-2017-1000103
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-63cj-3r94-234v
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:dry` — affected >=0 <2.49

## Details
The custom Details view of the Static Analysis Utilities based DRY Plugin, was vulnerable to a persisted cross-site scripting vulnerability: Malicious users able to influence the input to this plugin could insert arbitrary HTML into this view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000103
- https://jenkins.io/security/advisory/2017-08-07
- http://www.securityfocus.com/bid/101061
