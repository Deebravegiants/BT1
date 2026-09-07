# [M] Cross-Site Request Forgery (CSRF) vulnerability in Jenkins global-build-stats plugin

## Summary
Severity: Medium
Advisory: GHSA-gw8g-hh47-q4gw
CVE: CVE-2017-1000389
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gw8g-hh47-q4gw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:global-build-stats` — affected >=0 <1.5

## Details
Some URLs provided by Jenkins global-build-stats plugin version 1.4 and earlier returned a JSON response that contained request parameters. These responses had the Content Type: text/html, so could have been interpreted as HTML by clients, resulting in a potential reflected cross-site scripting vulnerability. Additionally, some URLs provided by global-build-stats plugin that modify data did not require POST requests to be sent, resulting in a potential cross-site request forgery vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000389
- https://jenkins.io/security/advisory/2017-10-23
