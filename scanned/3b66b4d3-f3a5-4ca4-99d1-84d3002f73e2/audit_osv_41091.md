# [H] Stirling-PDF: Internal Service Account API Key Disclosure via Pipeline Endpoint

## Summary
Severity: High
Advisory: CVE-2026-57485
Aliases: GHSA-3xxh-mm3g-c9w5
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-57485
Type: osv

## Details
Stirling-PDF is a locally hosted web application that facilitates various operations on PDF files. Prior to 2.9.0, the /api/v1/pipeline/handleData endpoint in app/core/src/main/java/stirling/software/SPDF/controller/api/pipeline/PipelineProcessor.java injects the STIRLING-PDF-BACKEND-API-USER API key into pipeline subrequests, allowing an authenticated ROLE_USER to retrieve the key through /api/v1/user/get-api-key, impersonate the internal service account, bypass normal rate limits, and access internal endpoints including /api/v1/info/requests/all and /api/v1/info/load/all. This issue is fixed in version 2.9.0.

## References
- https://github.com/Stirling-Tools/Stirling-PDF/releases/tag/v2.9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57485.json
- https://github.com/Stirling-Tools/Stirling-PDF/security/advisories/GHSA-3xxh-mm3g-c9w5
- https://nvd.nist.gov/vuln/detail/CVE-2026-57485
- https://github.com/Stirling-Tools/Stirling-PDF/commit/de9625942bbc329fdefcfde161476a633a3b3213
- https://github.com/Stirling-Tools/Stirling-PDF/pull/6047
