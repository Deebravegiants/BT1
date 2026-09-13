# [H] ChakraCore RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-qfcq-4vv7-9mq7
CVE: CVE-2017-11911
CWE: CWE-119
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qfcq-4vv7-9mq7
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.7.5

## Details
ChakraCore and Windows 10 1511, 1607, 1703, 1709, and Windows Server 2016 allows an attacker to execute arbitrary code in the context of the current user, due to how the scripting engine handles objects in memory, aka "Scripting Engine Memory Corruption Vulnerability". This CVE ID is unique from CVE-2017-11886, CVE-2017-11889, CVE-2017-11890, CVE-2017-11893, CVE-2017-11894, CVE-2017-11895, CVE-2017-11901, CVE-2017-11903, CVE-2017-11905, CVE-2017-11905, CVE-2017-11907, CVE-2017-11908, CVE-2017-11909, CVE-2017-11910, CVE-2017-11912, CVE-2017-11913, CVE-2017-11914, CVE-2017-11916, CVE-2017-11918, and CVE-2017-11930.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11911
- https://github.com/chakra-core/ChakraCore/pull/4411
- https://github.com/chakra-core/ChakraCore/commit/a5d6be626305671166f21db359c1c06a3a372b8b
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11911
- https://web.archive.org/web/20210124122722/http://www.securityfocus.com/bid/102087
- https://web.archive.org/web/20210829201729/http://www.securitytracker.com/id/1039990
- https://www.exploit-db.com/exploits/43468
