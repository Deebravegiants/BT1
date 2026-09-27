# [H] Chakra Scripting Engine RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-g8q3-rcf9-qx4q
CVE: CVE-2019-1024
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g8q3-rcf9-qx4q
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.10

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge (HTML-based). The vulnerability could corrupt memory in such a way that an attacker could execute arbitrary code in the context of the current user. An attacker who successfully exploited the vulnerability could gain the same user rights as the current user. If the current user is logged on with administrative user rights, an attacker who successfully exploited the vulnerability could take control of an affected system. An attacker could then install programs; view, change, or delete data; or create new accounts with full user rights.

In a web-based attack scenario, an attacker could host a specially crafted website that is designed to exploit the vulnerability through Microsoft Edge (HTML-based) and then convince a user to view the website. The attacker could also take advantage of compromised websites and websites that accept or host user-provided content or advertisements. These websites could contain specially crafted content that could exploit the vulnerability.

The security update addresses the vulnerability by modifying how the Chakra scripting engine handles objects in memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1024
- https://github.com/chakra-core/ChakraCore/commit/06a1438bd30957b3e0d8f19c7f65b1aadc5f5ef2
- https://github.com/chakra-core/ChakraCore/commit/3d6226cc2d1077537220361c82e34a362c6c76ee
- https://github.com/chakra-core/ChakraCore
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2019-1024
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1024
