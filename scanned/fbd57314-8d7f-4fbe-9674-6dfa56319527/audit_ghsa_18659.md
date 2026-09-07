# [C] DNN Insufficient Access Control - Image Upload allows for Site Content Overwrite

## Summary
Severity: Critical
Advisory: GHSA-3m8r-w7xg-jqvw
CVE: CVE-2025-64095
CWE: CWE-434
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-3m8r-w7xg-jqvw
Type: github-advisory

## Affected
- NuGet: `DNN.PLATFORM` — affected >=0 <10.1.1

## Details
### Summary
The default HTML editor provider allows unauthenticated file uploads and images can overwrite existing files.

### Description
An unauthenticated user can upload and replace existing files allowing defacing a website and combined with other issue, injection XSS payloads.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-3m8r-w7xg-jqvw
- https://nvd.nist.gov/vuln/detail/CVE-2025-64095
- https://github.com/dnnsoftware/Dnn.Platform
