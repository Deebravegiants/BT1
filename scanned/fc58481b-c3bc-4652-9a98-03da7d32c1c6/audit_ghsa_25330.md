# [M] CSRF vulnerability in Jenkins FTP publisher Plugin

## Summary
Severity: Medium
Advisory: GHSA-wg7x-vf54-9qjw
CVE: CVE-2019-1003058
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wg7x-vf54-9qjw
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:ftppublisher` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins FTP publisher Plugin in the FTPPublisher.DescriptorImpl#doLoginCheck method allows attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003058
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-974
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
