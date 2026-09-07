# [H] XML external entity (XXE) vulnerability in Jenkins

## Summary
Severity: High
Advisory: GHSA-qj27-w92h-fc9r
CVE: CVE-2015-1809
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qj27-w92h-fc9r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.597 <1.600
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.596.1

## Details
XML external entity (XXE) vulnerability in Jenkins before 1.600 and LTS before 1.596.1 allows remote attackers to read arbitrary XML files via an XPath query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1809
- https://bugzilla.redhat.com/show_bug.cgi?id=1205625
- https://jenkins.io/security/advisory/2015-02-27
