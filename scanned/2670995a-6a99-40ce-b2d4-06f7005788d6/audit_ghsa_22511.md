# [H] Jenkins TraceTronic ECU-TEST Plugin Man in the middle vulnerability

## Summary
Severity: High
Advisory: GHSA-w86j-99wg-r29f
CVE: CVE-2018-1999025
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-w86j-99wg-r29f
Type: github-advisory

## Affected
- Maven: `de.tracetronic.jenkins.plugins:ecutest` — affected >=0 <2.4

## Details
A man in the middle vulnerability exists in Jenkins TraceTronic ECU-TEST Plugin 2.3 and earlier in ATXPublisher.java, ATXValidator.java that allows attackers to impersonate any service that Jenkins connects to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999025
- https://github.com/jenkinsci/ecutest-plugin/commit/d2b730c0e1c986d53d8d48c0cd5bb9a3b205a2bb
- https://github.com/jenkinsci/ecutest-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-932
