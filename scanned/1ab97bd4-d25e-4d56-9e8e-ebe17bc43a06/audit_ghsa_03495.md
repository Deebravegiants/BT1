# [H] Out-of-bounds write

## Summary
Severity: High
Advisory: GHSA-7423-5qfm-g648
CVE: CVE-2019-0916
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-7423-5qfm-g648
Type: github-advisory

## Affected
- NuGet: `Microsoft.ChakraCore` — affected >=0 <1.11.9

## Details
A remote code execution vulnerability exists in the way that the Chakra scripting engine handles objects in memory in Microsoft Edge, aka 'Chakra Scripting Engine Memory Corruption Vulnerability'. This CVE ID is unique from CVE-2019-0912, CVE-2019-0913, CVE-2019-0914, CVE-2019-0915, CVE-2019-0917, CVE-2019-0922, CVE-2019-0923, CVE-2019-0924, CVE-2019-0925, CVE-2019-0927, CVE-2019-0933, CVE-2019-0937.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0916
- https://github.com/chakra-core/ChakraCore/commit/d797e3f00e34c12c8c0ae52f56344325439dccd7
- https://github.com/chakra-core/ChakraCore/commit/d85b5025b047f10784c53c6c1dd771775d417f5f
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0916
