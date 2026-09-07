# [H] CSRF vulnerability in Jenkins Orka Plugin allow capturing credentials

## Summary
Severity: High
Advisory: GHSA-9jwh-qvg7-gr59
CVE: CVE-2023-24432
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-9jwh-qvg7-gr59
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:macstadium-orka` — affected >=0 <1.32

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Orka by MacStadium Plugin 1.31 and earlier allows attackers to connect to an attacker-specified HTTP server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24432
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2772%20(2)
