# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-ch84-pxpj-7hhm
CVE: CVE-2018-8283
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-ch84-pxpj-7hhm
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.10.1

## Details
A remote code execution vulnerability exists in the way that the ChakraCore scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability." This affects ChakraCore. This CVE ID is unique from CVE-2018-8242, CVE-2018-8287, CVE-2018-8288, CVE-2018-8291, CVE-2018-8296, CVE-2018-8298.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8283
- https://github.com/chakra-core/ChakraCore/pull/5444
- https://github.com/chakra-core/ChakraCore/commit/b2f092ea42744d569fd102e8dd85d5524269bdd0
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8283
- https://web.archive.org/web/20210125211350/http://www.securityfocus.com/bid/104633
