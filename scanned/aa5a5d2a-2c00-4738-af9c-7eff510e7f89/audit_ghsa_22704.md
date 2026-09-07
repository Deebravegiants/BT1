# [M] CSRF vulnerability in Jenkins SOASTA CloudTest Plugin

## Summary
Severity: Medium
Advisory: GHSA-23r7-hf6g-qqqg
CVE: CVE-2019-1003090
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-23r7-hf6g-qqqg
Type: github-advisory

## Affected
- Maven: `com.soasta.jenkins:cloudtest` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins SOASTA CloudTest Plugin in the CloudTestServer.DescriptorImpl#doValidate form validation method allows attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003090
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1054
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
