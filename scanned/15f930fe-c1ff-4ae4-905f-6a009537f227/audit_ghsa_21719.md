# [M] Request logging bypass in Jenkins Audit Trail Plugin

## Summary
Severity: Medium
Advisory: GHSA-rpj6-2q8r-98f8
CVE: CVE-2020-2287
CWE: CWE-435
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-rpj6-2q8r-98f8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:audit-trail` — affected >=0 <3.7

## Details
Audit Trail Plugin logs requests whose URL path matches an admin-configured regular expression.

A discrepancy between the behavior of the plugin and the Stapler web framework in parsing URL paths allows attackers to craft URLs that would bypass request logging in Audit Trail Plugin 3.6 and earlier. This only applies to Jenkins 2.227 and earlier, LTS 2.204.5 and earlier, as the fix for [SECURITY-1774](https://www.jenkins.io/security/advisory/2020-03-25/#SECURITY-1774) prohibits dispatch of affected requests.

Audit Trail Plugin 3.7 processes request URL paths the same way as the Stapler web framework.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2287
- https://github.com/jenkinsci/audit-trail-plugin/commit/329c6090c1c444a16e95757e537b0cbb2347a9f4
- https://github.com/jenkinsci/audit-trail-plugin
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-1815
- http://www.openwall.com/lists/oss-security/2020/10/08/5
