# [M] DNN vulnerable to Reflected Cross-Site Scripting (XSS) using url to profile

## Summary
Severity: Medium
Advisory: GHSA-jc4g-c8ww-5738
CVE: CVE-2025-59821
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-09-23
Source: https://github.com/advisories/GHSA-jc4g-c8ww-5738
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <10.1.0

## Details
# Summary
A reflected cross-site scripting (XSS) vulnerability exists under certain conditions, using a specially crafter url to view a user profile

# Description
DNN’s URL/path handling and template rendering can allow specially crafted input to be reflected into a user profile that are returned to the browser. In these cases, the application does not sufficiently neutralize or encode characters that are meaningful in HTML, so an attacker can cause a victim’s browser to interpret attacker-controlled content as part of the page’s HTML.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-jc4g-c8ww-5738
- https://nvd.nist.gov/vuln/detail/CVE-2025-59821
- https://github.com/dnnsoftware/Dnn.Platform
