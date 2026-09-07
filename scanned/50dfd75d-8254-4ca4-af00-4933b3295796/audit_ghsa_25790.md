# [H] Cross site request forgery in Jenkins Job and Node ownership Plugin

## Summary
Severity: High
Advisory: GHSA-85f9-w9cx-h363
CVE: CVE-2022-28150
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-85f9-w9cx-h363
Type: github-advisory

## Affected
- Maven: `com.synopsys.jenkinsci:ownership` — affected >=0

## Details
Job and Node ownership Plugin 0.13.0 and earlier does not perform a permission check in several HTTP endpoints. This allows attackers with Item/Read permission to change the owners and item-specific permissions of a job. Additionally, this endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28150
- https://github.com/jenkinsci/ownership-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2062%20(1)
- http://www.openwall.com/lists/oss-security/2022/03/29/1
