# [M] DNN.PLATFORM Allows Stored Cross-Site Scripting (XSS) in Activity Feed

## Summary
Severity: Medium
Advisory: GHSA-wwc9-wmm3-2pmf
CVE: CVE-2025-52485
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-wwc9-wmm3-2pmf
Type: github-advisory

## Affected
- NuGet: `DNN.PLATFORM` — affected >=6.0.0 <10.0.1

## Details
DNN.PLATFORM allows a specially crafted request can inject scripts in the Activity Feed Attachments endpoint which will then render in the feed, resulting in a cross-site scripting attack. This vulnerability is fixed in 10.0.1.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-wwc9-wmm3-2pmf
- https://nvd.nist.gov/vuln/detail/CVE-2025-52485
- https://github.com/dnnsoftware/Dnn.Platform
