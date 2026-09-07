# [M] Jenkins mabl Plugin vulnerable to cross-site request forgery

## Summary
Severity: Medium
Advisory: GHSA-wvgr-5wgr-c6fj
CVE: CVE-2023-37952
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-wvgr-5wgr-c6fj
Type: github-advisory

## Affected
- Maven: `com.mabl.integration.jenkins:mabl-integration` — affected >=0 <0.0.47

## Details
Jenkins mabl Plugin 0.0.46 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, these HTTP endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

mabl Plugin 0.0.47 requires POST requests and the appropriate permissions for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37952
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3127
- http://www.openwall.com/lists/oss-security/2023/07/12/2
