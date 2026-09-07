# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-294j-r53x-w786
CVE: CVE-2016-3389
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-294j-r53x-w786
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.2.1

## Details
The Chakra JavaScript engine in Microsoft Edge allows remote attackers to execute arbitrary code or cause a denial of service (memory corruption) via a crafted web site, aka "Scripting Engine Memory Corruption Vulnerability," a different vulnerability than CVE-2016-3386, CVE-2016-7190, and CVE-2016-7194.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3389
- https://github.com/chakra-core/ChakraCore/pull/1737
- https://github.com/chakra-core/ChakraCore/commit/f05c42e64c3b2d057ae1a52fe1917af26c9f2737
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-119
- https://github.com/chakra-core/ChakraCore
- https://web.archive.org/web/20210123174706/http://www.securityfocus.com/bid/93398
- https://web.archive.org/web/20211208062350/http://www.securitytracker.com/id/1036993
