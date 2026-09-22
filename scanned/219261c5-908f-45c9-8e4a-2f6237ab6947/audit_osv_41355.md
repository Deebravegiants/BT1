# [M] Cap - Missing Access Control in Video AI Metadata Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-59704
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-59704
Type: osv

## Details
Cap's GET /api/video/ai endpoint fails to validate user ownership or membership before returning private video AI metadata including titles, summaries, and chapters. Authenticated attackers can supply arbitrary video IDs to read sensitive AI-generated content and trigger unauthorized AI generation that consumes the video owner's credits without consent.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59704.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59704
- https://www.vulncheck.com/advisories/cap-missing-access-control-in-video-ai-metadata-endpoint
- https://github.com/CapSoftware/Cap/issues/1981
- https://github.com/CapSoftware/Cap/pull/1926
- https://github.com/CapSoftware/Cap/commit/8d48642b6e7938af238386383ef1c273be4110dd
- https://github.com/CapSoftware/Cap
