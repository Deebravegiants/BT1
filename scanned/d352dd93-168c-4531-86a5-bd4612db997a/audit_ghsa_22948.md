# [H] Jenkins Team Concert Plugin missing permission check

## Summary
Severity: High
Advisory: GHSA-c998-c4f6-vjw2
CVE: CVE-2019-16566
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c998-c4f6-vjw2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:teamconcert` — affected >=0

## Details
Jenkins Team Concert Plugin 1.3.0 and earlier does not perform permission checks on a method implementing form validation. This allows users with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, the form validation method does not require POST requests, resulting in a CSRF vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16566
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1605%20%281%29
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1605%20(1)
- http://www.openwall.com/lists/oss-security/2019/12/17/1
