# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-h9cr-2hcf-cg8p
CVE: CVE-2018-8543
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h9cr-2hcf-cg8p
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.3

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka "Chakra Scripting Engine Memory Corruption Vulnerability." This affects Microsoft Edge, ChakraCore. This CVE ID is unique from CVE-2018-8541, CVE-2018-8542, CVE-2018-8551, CVE-2018-8555, CVE-2018-8556, CVE-2018-8557, CVE-2018-8588.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8543
- https://github.com/chakra-core/ChakraCore/pull/5827
- https://github.com/chakra-core/ChakraCore/commit/ef75eace57c0754428699485f10970ca0fb7a54d
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8543
- https://web.archive.org/web/20210730063716/http://www.securityfocus.com/bid/105846
- https://web.archive.org/web/20211126224439/http://www.securitytracker.com/id/1042107
