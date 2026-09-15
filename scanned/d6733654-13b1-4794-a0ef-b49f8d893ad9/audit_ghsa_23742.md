# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-jv5x-p843-g4qr
CVE: CVE-2018-8229
CWE: CWE-843
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jv5x-p843-g4qr
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.5

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka "Chakra Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2018-8227.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8229
- https://github.com/chakra-core/ChakraCore/commit/9b270c55bfea2fbefc9482d3414c4b4b395cad10
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8229
- https://web.archive.org/web/20210124174715/http://www.securityfocus.com/bid/104369
- https://web.archive.org/web/20210927135934/http://www.securitytracker.com/id/1041097
- https://www.exploit-db.com/exploits/45013
