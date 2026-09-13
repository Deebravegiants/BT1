# [H] Soot Infinite Loop vulnerability

## Summary
Severity: High
Advisory: GHSA-hfg7-j82c-fr3w
CVE: CVE-2023-46442
CWE: CWE-400, CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-24
Source: https://github.com/advisories/GHSA-hfg7-j82c-fr3w
Type: github-advisory

## Affected
- Maven: `org.soot-oss:soot` — affected >=0 <4.4.1

## Details
An infinite loop in the retrieveActiveBody function of Soot before v4.4.1 under Java 8 allows attackers to cause a Denial of Service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46442
- https://github.com/JAckLosingHeart/CVE-2023-46442_POC/tree/main
- https://github.com/soot-oss/soot
