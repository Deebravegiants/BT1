# [M] Missing permission check in Jenkins Job and Node ownership Plugin

## Summary
Severity: Medium
Advisory: GHSA-25f2-wgxj-ph29
CVE: CVE-2022-28151
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-25f2-wgxj-ph29
Type: github-advisory

## Affected
- Maven: `com.synopsys.jenkinsci:ownership` — affected >=0

## Details
A missing permission check in Jenkins Job and Node ownership Plugin 0.13.0 and earlier allows attackers with Item/Read permission to change the owners and item-specific permissions of a job.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28151
- https://github.com/jenkinsci/ownership-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2062%20(1)
- http://www.openwall.com/lists/oss-security/2022/03/29/1
