# [M] ChakraCore information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w3qr-8v4r-592m
CVE: CVE-2018-8452
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w3qr-8v4r-592m
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.1

## Details
An information disclosure vulnerability exists when the scripting engine does not properly handle objects in memory in Microsoft browsers, aka "Scripting Engine Information Disclosure Vulnerability." This affects ChakraCore, Internet Explorer 11, Microsoft Edge.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8452
- https://github.com/chakra-core/ChakraCore/commit/3f3544801cc01e9f54cab84b20602a3b5e29c3ef
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8452
- https://web.archive.org/web/20210124203129/http://www.securityfocus.com/bid/105252
- https://web.archive.org/web/20221128100304/http://www.securitytracker.com/id/1041623
