# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-j69r-w67w-gf35
CVE: CVE-2016-0191
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j69r-w67w-gf35
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.2.0.0

## Details
The Chakra JavaScript engine in Microsoft Edge allows remote attackers to execute arbitrary code or cause a denial of service (memory corruption) via a crafted web site, aka "Scripting Engine Memory Corruption Vulnerability," a different vulnerability than CVE-2016-0186 and CVE-2016-0193.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0191
- https://github.com/chakra-core/ChakraCore/commit/d21529b131d831fc4470139bfc90d80ae7481fa2
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-052
- https://github.com/chakra-core/ChakraCore
- https://web.archive.org/web/20201024061334/http://www.securitytracker.com/id/1035821
- https://web.archive.org/web/20210123133443/http://www.securityfocus.com/bid/90010
- http://www.zerodayinitiative.com/advisories/ZDI-16-282
