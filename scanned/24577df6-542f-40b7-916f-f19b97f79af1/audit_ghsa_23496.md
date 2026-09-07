# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-fv8m-p45w-gf38
CVE: CVE-2018-0818
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fv8m-p45w-gf38
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.8.0

## Details
Microsoft ChakraCore allows an attacker to bypass Control Flow Guard (CFG) in conjunction with another vulnerability to run arbitrary code on a target system, due to how the Chakra scripting engine handles accessing memory, aka "Scripting Engine Security Feature Bypass".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0818
- https://github.com/chakra-core/ChakraCore/pull/4427
- https://github.com/chakra-core/ChakraCore/pull/4427/commits/84368681cf5cf1d33364638e2cd463ad1b13eba6
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0818
- https://web.archive.org/web/20210124130147/http://www.securityfocus.com/bid/102412
