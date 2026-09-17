# [C] FastGPT: Unauthenticated SSRF via httpTools Endpoint Leads to Internal API Key Theft

## Summary
Severity: Critical
Advisory: CVE-2026-34162
Aliases: GHSA-w36r-f268-pwrj
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34162
Type: osv

## Details
FastGPT is an AI Agent building platform. Prior to version 4.14.9.5, the FastGPT HTTP tools testing endpoint (/api/core/app/httpTools/runTool) is exposed without any authentication. This endpoint acts as a full HTTP proxy — it accepts a user-supplied baseUrl, toolPath, HTTP method, custom headers, and body, then makes a server-side HTTP request and returns the complete response to the caller. This issue has been patched in version 4.14.9.5.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.14.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34162.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-w36r-f268-pwrj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34162
- https://github.com/labring/FastGPT/commit/bc7eae2ed61481a5e322208829be291faec58c00
- https://github.com/labring/FastGPT/pull/6640
