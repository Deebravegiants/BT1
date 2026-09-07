# [C] File upload leading to RCE in MCMS

## Summary
Severity: Critical
Advisory: GHSA-g8j8-mgh9-q77p
CVE: CVE-2021-46036
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-19
Source: https://github.com/advisories/GHSA-g8j8-mgh9-q77p
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
An arbitrary file upload vulnerability in the component /ms/file/uploadTemplate.do of MCMS v5.2.4 allows attackers to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46036
- https://lycshub.github.io/2021/12/28/MCMS-vulnerabilities
