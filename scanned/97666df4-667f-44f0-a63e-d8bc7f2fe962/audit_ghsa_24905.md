# [M] Jenkins TraceTronic ECU-TEST Plugin server-side request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hp7x-282p-hhr9
CVE: CVE-2018-1999026
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hp7x-282p-hhr9
Type: github-advisory

## Affected
- Maven: `de.tracetronic.jenkins.plugins:ecutest` — affected >=0 <2.4

## Details
A server-side request forgery vulnerability exists in Jenkins TraceTronic ECU-TEST Plugin 2.3 and earlier in ATXPublisher.java that allows attackers to have Jenkins send HTTP requests to an attacker-specified host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999026
- https://github.com/jenkinsci/ecutest-plugin/commit/943c4d3c8df521eb94fb99429717e3920c6fc7f7
- https://github.com/jenkinsci/ecutest-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-994
- https://web.archive.org/web/20200227115310/http://www.securityfocus.com/bid/104960
