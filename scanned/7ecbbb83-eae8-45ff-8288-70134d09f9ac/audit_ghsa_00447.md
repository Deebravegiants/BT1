# [H] High severity vulnerability that affects DotNetNuke.Core

## Summary
Severity: High
Advisory: GHSA-g8j6-m4p7-5rfq
CVE: CVE-2017-0929
CWE: CWE-918
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-g8j6-m4p7-5rfq
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <9.2.0

## Details
DNN (aka DotNetNuke) before 9.2.0 suffers from a Server-Side Request Forgery (SSRF) vulnerability in the DnnImageHandler class. Attackers may be able to access information about internal network resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0929
- https://github.com/dnnsoftware/Dnn.Platform/commit/d3953db85fee77bb5e6383747692c507ef8b94c3
- https://github.com/advisories/GHSA-g8j6-m4p7-5rfq
- https://github.com/dnnsoftware/Dnn.Platform
