# [H] Chakra Core vulnerable to privilege escalation due to reading an invalid pointer

## Summary
Severity: High
Advisory: GHSA-43qp-hphf-5rjw
CVE: CVE-2017-11871
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-43qp-hphf-5rjw
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.7.4

## Details
ChakraCore and Microsoft Edge in Windows 10 1703, 1709, and Windows Server, version 1709 allows an attacker to gain the same user rights as the current user, due to how the scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability". When trying to get `inlineCache`s for a `ScriptFunctionWithInlineCache`, if the function got redefered and was not reparsed, the function body (and `inlineCache` on function body) won’t be there, potentially leading to a privilege escalation.

This CVE ID is unique from CVE-2017-11836, CVE-2017-11837, CVE-2017-11838, CVE-2017-11839, CVE-2017-11840, CVE-2017-11841, CVE-2017-11843, CVE-2017-11846, CVE-2017-11858, CVE-2017-11859, CVE-2017-11861, CVE-2017-11862, CVE-2017-11866, CVE-2017-11869, CVE-2017-11870, and CVE-2017-11873.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11871
- https://github.com/chakra-core/ChakraCore/pull/4226
- https://github.com/chakra-core/ChakraCore/commit/9d211a417757ba1ddcd0f2e72d9553535256107e
- https://github.com/chakra-core/ChakraCore
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11871
- https://web.archive.org/web/20210124114740/http://www.securityfocus.com/bid/101730
- https://web.archive.org/web/20210517135249/http://www.securitytracker.com/id/1039780
