# [M] Missing permission check in Jenkins Netsparker Cloud Scan Plugin

## Summary
Severity: Medium
Advisory: GHSA-whcg-2364-672f
CVE: CVE-2019-10290
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-whcg-2364-672f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:netsparker-cloud-scan` — affected >=0 <1.1.6

## Details
A missing permission check in Jenkins Netsparker Cloud Scan Plugin 1.1.5 and older in the NCScanBuilder.DescriptorImpl#doValidateAPI form validation method allowed attackers with Overall/Read permission to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10290
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-1032
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
