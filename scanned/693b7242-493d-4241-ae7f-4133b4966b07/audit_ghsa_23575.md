# [M] Missing permission check in Jenkins Docker Plugin

## Summary
Severity: Medium
Advisory: GHSA-76w6-m7vv-7hhw
CVE: CVE-2019-10341
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-76w6-m7vv-7hhw
Type: github-advisory

## Affected
- Maven: `io.jenkins.docker:docker-plugin` — affected >=0 <1.1.7

## Details
A missing permission check in Jenkins Docker Plugin 1.1.6 and earlier in DockerAPI.DescriptorImpl#doTestConnection allowed users with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10341
- https://github.com/jenkinsci/docker-plugin/commit/6ad27199f6fad230be72fd45da78ddac85c075db
- https://jenkins.io/security/advisory/2019-07-11/#SECURITY-1010
- http://www.openwall.com/lists/oss-security/2019/07/11/4
- http://www.securityfocus.com/bid/109156
