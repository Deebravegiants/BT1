# [M] Missing permission check in Jenkins Audit to Database Plugin

## Summary
Severity: Medium
Advisory: GHSA-492x-gfqx-wpf3
CVE: CVE-2019-1003077
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-492x-gfqx-wpf3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:audit2db` — affected >=0

## Details
A missing permission check in Jenkins Audit to Database Plugin in the DbAuditPublisherDescriptorImpl#doTestJdbcConnection form validation method allows attackers with Overall/Read permission to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003077
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-977
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
