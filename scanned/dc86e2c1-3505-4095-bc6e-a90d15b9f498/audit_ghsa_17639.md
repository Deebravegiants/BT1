# [M] DNN.PLATFORM Allows Reflected Cross-Site Scripting (XSS) in some TokenReplace situations with SkinObjects

## Summary
Severity: Medium
Advisory: GHSA-pf4h-vrv6-cmvr
CVE: CVE-2025-52486
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-pf4h-vrv6-cmvr
Type: github-advisory

## Affected
- NuGet: `DNN.PLATFORM` — affected >=6.0.0 <10.0.1

## Details
DNN.PLATFORM allows specially crafted content in URLs could be used with TokenReplace and not be properly sanitized by some SkinObjects. This vulnerability is fixed in 10.0.1.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-pf4h-vrv6-cmvr
- https://nvd.nist.gov/vuln/detail/CVE-2025-52486
- https://github.com/dnnsoftware/Dnn.Platform/commit/74f6de68da1572c1d7e9c6e30e9f77f7c5596b1b
- https://github.com/dnnsoftware/Dnn.Platform
