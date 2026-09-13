# [M] DNN CKEditor Provider allows unauthenticated upload out-of-the-box

## Summary
Severity: Medium
Advisory: GHSA-2374-6cvw-qmx6
CVE: CVE-2025-62802
CWE: CWE-434
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-2374-6cvw-qmx6
Type: github-advisory

## Affected
- NuGet: `Dnn.Platform` — affected >=0 <10.1.1

## Details
### Summary
The out-of-box experience for HTML editing allows unauthenticated users to upload files. This opens a potential vector to other security issues and is not needed on most implementations.

### Details
The new out-of-box experience blocks that endpoint to unauthenticated users. If there is a real need for the implementation to allow unauthenticated uploads, then the web.config can be edited by the implementer to remove that block and open the endpoint to the public.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-2374-6cvw-qmx6
- https://nvd.nist.gov/vuln/detail/CVE-2025-62802
- https://github.com/dnnsoftware/Dnn.Platform/commit/6497d3c35217e6e62e50d3ed7c8809eb69e3d06b
- https://github.com/dnnsoftware/Dnn.Platform
