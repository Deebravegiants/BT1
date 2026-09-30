# [M] Directory Traversal in Gladys Assistant

## Summary
Severity: Medium
Advisory: GHSA-c79f-pqgf-fhp3
CVE: CVE-2023-47440
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-07
Source: https://github.com/advisories/GHSA-c79f-pqgf-fhp3
Type: github-advisory

## Affected
- npm: `gladys` — affected >=0

## Details
Gladys Assistant v4.27.0 and prior is vulnerable to Directory Traversal. The patch of CVE-2023-43256 was found to be incomplete, allowing authenticated attackers to extract sensitive files in the host machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47440
- https://github.com/GladysAssistant/Gladys/pull/1918/commits/4f56ba250ff9f46578f1afa6a97e62e74bad83b7
- https://blog.moku.fr/cve
- https://blog.moku.fr/cves/CVE-2023-47440
- https://github.com/GladysAssistant/Gladys
