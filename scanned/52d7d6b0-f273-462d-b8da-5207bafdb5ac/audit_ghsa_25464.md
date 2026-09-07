# [M] CSRF vulnerability in Jenkins Netsparker Enterprise Scan Plugin

## Summary
Severity: Medium
Advisory: GHSA-qc3m-6xmq-7hrj
CVE: CVE-2019-10289
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qc3m-6xmq-7hrj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:netsparker-cloud-scan` — affected >=0 <1.1.6

## Details
A cross-site request forgery vulnerability in Jenkins Netsparker Cloud Scan Plugin 1.1.5 and older in the NCScanBuilder.DescriptorImpl#doValidateAPI form validation method allowed attackers to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10289
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1032
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
