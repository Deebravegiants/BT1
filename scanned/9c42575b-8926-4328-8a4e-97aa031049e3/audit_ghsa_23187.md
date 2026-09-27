# [H] Chakra Scripting Engine and ChakraCore Vulnerable to Memory Corruption

## Summary
Severity: High
Advisory: GHSA-jgrp-6qqq-3284
CVE: CVE-2021-42279
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jgrp-6qqq-3284
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0

## Details
Chakra Scripting Engine and ChakraCore are vulnerable to memory corruption due to an out-of-bounds write. The Microsoft advisory for CVE-2021-42279 was modified in August 2022 to include Microsoft.ChakraCore as an affected product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42279
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2021-42279
