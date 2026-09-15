# [M] Missing permission checks in Jenkins Orka Plugin allow capturing credentials

## Summary
Severity: Medium
Advisory: GHSA-gmhf-37fx-c4q8
CVE: CVE-2023-24433
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-gmhf-37fx-c4q8
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:macstadium-orka` — affected >=0 <1.32

## Details
Missing permission checks in Jenkins Orka by MacStadium Plugin 1.31 and earlier allow attackers with Overall/Read permission to connect to an attacker-specified HTTP server using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24433
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2772%20(2)
