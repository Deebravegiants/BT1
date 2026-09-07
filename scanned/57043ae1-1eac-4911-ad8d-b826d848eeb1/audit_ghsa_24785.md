# [M] Jenkins VMware Lab Manager Slaves Plugin vulnerable CSRF vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6j5j-w6v4-rwqr
CVE: CVE-2019-1003078
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6j5j-w6v4-rwqr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:labmanager` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins VMware Lab Manager Slaves Plugin in the LabManager.DescriptorImpl#doTestConnection form validation method allows attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003078
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-979
- http://www.securityfocus.com/bid/107790
