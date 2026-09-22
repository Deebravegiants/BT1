# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-5whg-j5fv-xcm2
CVE: CVE-2016-7200
CWE: CWE-119, CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5whg-j5fv-xcm2
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.2.2

## Details
The Chakra JavaScript scripting engine in Microsoft Edge allows remote attackers to execute arbitrary code or cause a denial of service (memory corruption) via a crafted web site, aka "Scripting Engine Memory Corruption Vulnerability," a different vulnerability than CVE-2016-7201, CVE-2016-7202, CVE-2016-7203, CVE-2016-7208, CVE-2016-7240, CVE-2016-7242, and CVE-2016-7243.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7200
- https://github.com/chakra-core/ChakraCore/pull/1982
- https://github.com/chakra-core/ChakraCore/commit/c2787ef8fdb7401922e9ec6540e4e5895d11c631
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2016/ms16-129
- https://github.com/chakra-core/ChakraCore
- https://github.com/theori-io/chakra-2016-11
- https://web.archive.org/web/20210123184454/http://www.securityfocus.com/bid/93968
- https://web.archive.org/web/20211126224744/http://www.securitytracker.com/id/1037245
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2016-7200
- https://www.exploit-db.com/exploits/40785
- https://www.exploit-db.com/exploits/40990
- http://packetstormsecurity.com/files/140382/Microsoft-Edge-chakra.dll-Information-Leak-Type-Confusion.html
- http://www.securityfocus.com/bid/93968
- http://www.securitytracker.com/id/1037245
