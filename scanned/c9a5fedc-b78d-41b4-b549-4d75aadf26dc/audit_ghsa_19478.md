# [M] DotNetNuke.Core Vulnerable to Server-Side Request Forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-3f7v-qx94-666m
CVE: CVE-2025-32372
CWE: CWE-918
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-3f7v-qx94-666m
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <9.13.8

## Details
A bypass has been identified for the previously known vulnerability CVE-2017-0929, allowing unauthenticated attackers to execute arbitrary GET requests against target systems, including internal or adjacent networks.

### Impact

This vulnerability facilitates a semi-blind SSRF attack, allowing attackers to make the target server send requests to internal or external URLs without viewing the full responses. Potential impacts include internal network reconnaissance, bypassing firewalls.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-3f7v-qx94-666m
- https://nvd.nist.gov/vuln/detail/CVE-2025-32372
- https://github.com/dnnsoftware/Dnn.Platform/commit/4721dd9eef846936d3b1a3676499e46968d15feb
- https://github.com/dnnsoftware/Dnn.Platform
