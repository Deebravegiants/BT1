# [H] SSL/TLS certificate validation disabled by default in Jenkins Checkmarx Plugin

## Summary
Severity: High
Advisory: GHSA-rr3p-5fcf-v5m3
CVE: CVE-2023-35142
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-rr3p-5fcf-v5m3
Type: github-advisory

## Affected
- Maven: `com.checkmarx.jenkins:checkmarx` — affected >=0 <2023.2.6

## Details
Jenkins Checkmarx Plugin 2022.4.3 and earlier disables SSL/TLS validation for connections to the Checkmarx server by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35142
- https://www.jenkins.io/security/advisory/2023-06-14/#SECURITY-2870
- http://www.openwall.com/lists/oss-security/2023/06/14/5
