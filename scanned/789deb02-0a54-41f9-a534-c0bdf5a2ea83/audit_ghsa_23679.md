# [M] ChakraCore Security Bypass

## Summary
Severity: Medium
Advisory: GHSA-wg47-6cqc-q52j
CVE: CVE-2018-8276
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wg47-6cqc-q52j
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.10.1

## Details
A security feature bypass vulnerability exists in the Microsoft Chakra scripting engine that allows Control Flow Guard (CFG) to be bypassed, aka "Scripting Engine Security Feature Bypass Vulnerability." This affects Microsoft Edge, ChakraCore.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8276
- https://github.com/chakra-core/ChakraCore/commit/4196f8097afdcc5fe01ce2966871712fb24003a3
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8276
- https://web.archive.org/web/20210124183457/http://www.securityfocus.com/bid/104626
- https://web.archive.org/web/20211202002348/http://www.securitytracker.com/id/1041256
