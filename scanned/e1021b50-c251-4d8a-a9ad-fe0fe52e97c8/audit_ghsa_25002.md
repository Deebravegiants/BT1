# [H] Chakra Core vulnerable to privilege escalation due to type confusion

## Summary
Severity: High
Advisory: GHSA-pcr8-75v3-w9pf
CVE: CVE-2017-11862
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pcr8-75v3-w9pf
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.7.4

## Details
ChakraCore and Microsoft Edge in Windows 10 1709 and Windows Server, version 1709 allows an attacker to gain the same user rights as the current user, due to how the scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability". Individual Export in module exports was not taking care of destructuring nodes, leading to type confusion. This was fixed by adding support for walking those nodes.

This CVE ID is unique from CVE-2017-11836, CVE-2017-11837, CVE-2017-11838, CVE-2017-11839, CVE-2017-11840, CVE-2017-11841, CVE-2017-11843, CVE-2017-11846, CVE-2017-11858, CVE-2017-11859, CVE-2017-11861, CVE-2017-11866, CVE-2017-11869, CVE-2017-11870, CVE-2017-11871, and CVE-2017-11873.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11862
- https://github.com/chakra-core/ChakraCore/pull/4226
- https://github.com/chakra-core/ChakraCore/commit/66d733b9adebbe33cc7f48c159c48b7837aa4458
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11862
- https://web.archive.org/web/20210124114723/http://www.securityfocus.com/bid/101724
- https://web.archive.org/web/20210517135249/http://www.securitytracker.com/id/1039780
