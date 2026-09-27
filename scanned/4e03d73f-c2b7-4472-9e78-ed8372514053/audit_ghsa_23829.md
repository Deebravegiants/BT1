# [M] Jenkins Swarm Plugin Client vulnerable to man-in-the-middle attacks

## Summary
Severity: Medium
Advisory: GHSA-pj45-8vhc-mh2f
CVE: CVE-2017-1000402
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pj45-8vhc-mh2f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:swarm-client` — affected >=0 <3.5
- Maven: `org.jvnet.hudson.plugins:swarm-plugin` — affected >=0

## Details
Jenkins Swarm Plugin Client 3.4 and earlier bundled a version of the commons-httpclient library with the vulnerability CVE-2012-6153 that incorrectly verified SSL certificates, making it susceptible to man-in-the-middle attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000402
- https://jenkins.io/security/advisory/2017-10-11
