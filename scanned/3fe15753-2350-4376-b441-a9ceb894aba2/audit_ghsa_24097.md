# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-923j-972p-hchf
CVE: CVE-2017-11908
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-923j-972p-hchf
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.7.5

## Details
ChakraCore and Windows 10 1709 allows an attacker to execute arbitrary code in the context of the current user, due to how the scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability". This CVE ID is unique from CVE-2017-11886, CVE-2017-11889, CVE-2017-11890, CVE-2017-11893, CVE-2017-11894, CVE-2017-11895, CVE-2017-11901, CVE-2017-11903, CVE-2017-11905, CVE-2017-11905, CVE-2017-11907, CVE-2017-11909, CVE-2017-11910, CVE-2017-11911, CVE-2017-11912, CVE-2017-11913, CVE-2017-11914, CVE-2017-11916, CVE-2017-11918, and CVE-2017-11930.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11908
- https://github.com/chakra-core/ChakraCore/pull/4411
- https://github.com/chakra-core/ChakraCore/commit/39eecff7daecce96088f7ed737f145ee4774faa6
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11908
- https://web.archive.org/web/20210124122457/http://www.securityfocus.com/bid/102052
- https://web.archive.org/web/20210829201729/http://www.securitytracker.com/id/1039990
