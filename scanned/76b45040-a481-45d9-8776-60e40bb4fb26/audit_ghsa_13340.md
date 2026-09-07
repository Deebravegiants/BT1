# [M] CSRF vulnerability in Bazaar Plugin 

## Summary
Severity: Medium
Advisory: GHSA-6f4q-f5fj-q6fc
CVE: CVE-2023-39156
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-6f4q-f5fj-q6fc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bazaar` — affected >=0

## Details
Jenkins Bazaar Plugin 1.22 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to delete previously created Bazaar SCM tags.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39156
- https://www.jenkins.io/security/advisory/2023-07-26/#SECURITY-3095
- http://www.openwall.com/lists/oss-security/2023/07/26/2
