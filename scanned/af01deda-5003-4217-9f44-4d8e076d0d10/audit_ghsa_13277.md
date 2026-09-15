# [M] Alkacon OpenCMS arbitrary file upload vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ghg2-3w9x-9599
CVE: CVE-2023-37602
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-20
Source: https://github.com/advisories/GHSA-ghg2-3w9x-9599
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=0

## Details
An arbitrary file upload vulnerability in the component /workplace#!explorer of Alkacon OpenCMS v15.0 allows attackers to execute arbitrary code via uploading a crafted PNG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37602
- https://github.com/alkacon/opencms-core
- https://www.exploit-db.com/exploits/51564
