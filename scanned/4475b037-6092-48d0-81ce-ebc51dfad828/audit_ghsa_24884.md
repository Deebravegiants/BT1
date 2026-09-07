# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-ggvv-6v25-r49r
CVE: CVE-2018-8384
CWE: CWE-843
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-ggvv-6v25-r49r
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.10.2

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka "Chakra Scripting Engine Memory Corruption Vulnerability." This affects ChakraCore. This CVE ID is unique from CVE-2018-8266, CVE-2018-8380, CVE-2018-8381.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8384
- https://github.com/chakra-core/ChakraCore/pull/5596
- https://github.com/chakra-core/ChakraCore/commit/765bcd2c801eedc07fd0a4e90f69d41c483aa74a
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8384
- https://web.archive.org/web/20210124194908/http://www.securityfocus.com/bid/104981
- https://www.exploit-db.com/exploits/45431
