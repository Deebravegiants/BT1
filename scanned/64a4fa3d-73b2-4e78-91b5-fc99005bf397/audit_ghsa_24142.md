# [H] Jenkins Pipeline Classpath Step plugin allowed Script Security sandbox bypass

## Summary
Severity: High
Advisory: GHSA-r5c7-qcc9-5v7m
CVE: CVE-2017-2650
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r5c7-qcc9-5v7m
Type: github-advisory

## Affected
- Maven: `cprice404:pipeline-classpath` — affected 0.1.0

## Details
It was found that the use of Pipeline: Classpath Step Jenkins plugin enables a bypass of the Script Security sandbox for users with SCM commit access, as well as users with e.g. Job/Configure permission in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2650
- https://jenkins.io/security/advisory/2017-03-20
- http://www.securityfocus.com/bid/96981
