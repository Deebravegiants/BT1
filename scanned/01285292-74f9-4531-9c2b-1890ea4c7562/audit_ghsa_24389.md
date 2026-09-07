# [H] Jenkins Docker Plugin contains Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-m6gf-p26p-mx2w
CVE: CVE-2019-10340
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m6gf-p26p-mx2w
Type: github-advisory

## Affected
- Maven: `io.jenkins.docker:docker-plugin` — affected >=0 <1.1.7

## Details
A cross-site request forgery vulnerability in Jenkins Docker Plugin 1.1.6 and earlier in DockerAPI.DescriptorImpl#doTestConnection allowed users with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10340
- https://github.com/jenkinsci/docker-plugin/commit/6ad27199f6fad230be72fd45da78ddac85c075db
- https://github.com/jenkinsci/docker-plugin
- https://jenkins.io/security/advisory/2019-07-11/#SECURITY-1010
- http://www.openwall.com/lists/oss-security/2019/07/11/4
- http://www.securityfocus.com/bid/109156
