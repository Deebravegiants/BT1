# [H] Missing permission checks in Jenkins Distributed Fork Plugin

## Summary
Severity: High
Advisory: GHSA-2cm5-f78c-h2c8
CVE: CVE-2017-2652
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2cm5-f78c-h2c8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:distfork` — affected >=0 <1.6.0

## Details
It was found that there were no permission checks performed in the Distributed Fork plugin before and including 1.5.0 for Jenkins that provides the dist-fork CLI command beyond the basic check for Overall/Read permission, allowing anyone with that permission to run arbitrary shell commands on all connected nodes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2652
- https://jenkins.io/security/advisory/2017-03-20
- http://www.securityfocus.com/bid/96980
