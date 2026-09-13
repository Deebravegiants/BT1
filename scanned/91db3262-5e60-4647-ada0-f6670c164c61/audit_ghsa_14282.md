# [M] Jenkins OctoPerf Load Testing Plugin vulnerable to credential capture

## Summary
Severity: Medium
Advisory: GHSA-j9h4-p6p7-8652
CVE: CVE-2023-28672
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-j9h4-p6p7-8652
Type: github-advisory

## Affected
- Maven: `org.jenkinsci.plugins:octoperf` — affected >=0 <4.5.2

## Details
OctoPerf Load Testing Plugin Plugin 4.5.1 and earlier does not perform a permission check in a connection test HTTP endpoint.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

OctoPerf Load Testing Plugin Plugin 4.5.2 properly performs a permission check when accessing the affected connection test HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28672
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-3067%20(2)
