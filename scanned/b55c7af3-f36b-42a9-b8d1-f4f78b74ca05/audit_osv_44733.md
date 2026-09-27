# [M] ms-swift 4.5.2 Unauthenticated SSRF via Multimodal Media URLs

## Summary
Severity: Medium
Advisory: CVE-2026-85686
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85686
Type: osv

## Details
ms-swift 4.5.2 contains a server-side request forgery vulnerability in the swift deploy OpenAI-compatible API that fetches multimodal media URLs without validation or redirect filtering. Unauthenticated attackers can supply arbitrary image_url, audio_url, or video_url parameters to make the server issue requests to internal services and cloud metadata endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85686.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85686
- https://www.vulncheck.com/advisories/ms-swift-4.5.2-unauthenticated-ssrf-via-multimodal-media-urls
- https://github.com/modelscope/ms-swift/issues/9740
- https://github.com/modelscope/ms-swift
- https://github.com/modelscope/ms-swift/blob/v4.5.2/swift/template/vision_utils.py
