# [H] Hash collision attack vulnerability in Jenkins

## Summary
Severity: High
Advisory: GHSA-pchp-c5w8-47gc
CVE: CVE-2012-0785
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-pchp-c5w8-47gc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.425 <1.447
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.424.2

## Details
Hash collision attack vulnerability in Jenkins before 1.447, Jenkins LTS before 1.424.2, and Jenkins Enterprise by CloudBees 1.424.x before 1.424.2.1 and 1.400.x before 1.400.0.11 could allow remote attackers to cause a considerable CPU load, aka "the Hash DoS attack."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-0785
- https://access.redhat.com/security/cve/cve-2012-0785
- https://jenkins.io/security/advisory/2012-01-12
- https://security-tracker.debian.org/tracker/CVE-2012-0785
- https://www.cloudbees.com/jenkins-security-advisory-2012-01-12
- http://www.openwall.com/lists/oss-security/2012/01/20/8
