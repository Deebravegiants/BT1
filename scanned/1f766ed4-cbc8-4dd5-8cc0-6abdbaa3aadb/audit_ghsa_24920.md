# [C] Deserialization of Untrusted Data in com.bstek.ureport:ureport2-console

## Summary
Severity: Critical
Advisory: GHSA-w39x-chvm-pj3c
CVE: CVE-2022-25767
CWE: CWE-502, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-w39x-chvm-pj3c
Type: github-advisory

## Affected
- Maven: `com.bstek.ureport:ureport2-console` — affected >=0

## Details
All versions of package com.bstek.ureport:ureport2-console are vulnerable to Remote Code Execution by connecting to a malicious database server, causing arbitrary file read and deserialization of local gadgets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25767
- https://github.com/JinYiTong/CVE-Req/blob/main/ureport2/ureport2-console.md
- https://github.com/youseries/ureport
- https://snyk.io/vuln/SNYK-JAVA-COMBSTEKUREPORT-2322018
