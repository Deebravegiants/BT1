# [M] Jenkins Orka by MacStadium Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-4hm4-94g6-f23f
CVE: CVE-2023-37949
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-4hm4-94g6-f23f
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:macstadium-orka` — affected >=0 <1.34

## Details
Jenkins Orka by MacStadium Plugin 1.33 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Orka by MacStadium Plugin 1.34 requires Overall/Administer permission to access the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37949
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3128
- http://www.openwall.com/lists/oss-security/2023/07/12/2
