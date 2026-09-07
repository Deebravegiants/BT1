# [M] Jenkins OctoPerf Load Testing Plugin vulnerable to Cross-site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-wq3w-3rxh-vcxx
CVE: CVE-2023-28671
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-wq3w-3rxh-vcxx
Type: github-advisory

## Affected
- Maven: `org.jenkinsci.plugins:octoperf` — affected >=0 <4.5.1

## Details
OctoPerf Load Testing Plugin Plugin 4.5.0 and earlier does not require POST requests for a connection test HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

OctoPerf Load Testing Plugin Plugin 4.5.1 requires POST requests for the affected connection test HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28671
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-3067%20(1)
