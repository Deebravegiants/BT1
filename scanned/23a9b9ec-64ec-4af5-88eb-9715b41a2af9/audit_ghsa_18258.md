# [M] DNN affected by Stored Cross-Site Scripting (XSS) in Profile Biography field

## Summary
Severity: Medium
Advisory: GHSA-7rcc-q6rq-jpcm
CVE: CVE-2025-59539
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-22
Source: https://github.com/advisories/GHSA-7rcc-q6rq-jpcm
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <10.1.0

## Details
## Summary
Users can use special syntax to inject javascript code in their profile biography field. Although there was sanitization in place, it did not cover all possible scenarios

## Description
When embedding information in the `Biography` field, even if that field is not rich-text, users could inject javascript code that would run in the context of the website and to any other user that can view the profile including administrators and/or superusers.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-7rcc-q6rq-jpcm
- https://nvd.nist.gov/vuln/detail/CVE-2025-59539
- https://github.com/dnnsoftware/Dnn.Platform
