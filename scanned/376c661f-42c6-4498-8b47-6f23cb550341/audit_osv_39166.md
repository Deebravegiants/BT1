# [H] FastGPT: SSRF Protection Bypass via `externalFile` in Dataset Preview API

## Summary
Severity: High
Advisory: CVE-2026-44285
Aliases: GHSA-c65v-7vx6-f8m3
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44285
Type: osv

## Details
FastGPT is an AI Agent building platform. Prior to 4.15.0-beta1, a Server-Side Request Forgery (SSRF) vulnerability allows an authenticated attacker to bypass the global isInternalAddress network protection and make arbitrary HTTP GET requests to internal network services. This is achieved by exploiting an incomplete fix in the dataset preview endpoint /api/core/dataset/file/getPreviewChunks when utilizing the externalFile data import type. This vulnerability is fixed in 4.15.0-beta1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44285.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-c65v-7vx6-f8m3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44285
