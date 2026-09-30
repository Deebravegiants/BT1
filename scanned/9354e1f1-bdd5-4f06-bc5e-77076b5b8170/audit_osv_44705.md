# [M] Douyin_TikTok_Download_API 4.1.2 SSRF via url parameter

## Summary
Severity: Medium
Advisory: CVE-2026-85608
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85608
Type: osv

## Details
Douyin_TikTok_Download_API through 4.1.2 contains a server-side request forgery vulnerability in the /api/download and /api/hybrid/video_data endpoints that allows unauthenticated attackers to fetch arbitrary URLs by supplying a url query parameter. Attackers can request internal services including cloud metadata endpoints and retrieve response bodies containing sensitive credentials through error messages.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85608.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85608
- https://www.vulncheck.com/advisories/douyin-tiktok-download-api-4.1.2-ssrf-via-url-parameter
- https://github.com/Evil0ctal/Douyin_TikTok_Download_API/issues/729
- https://github.com/Evil0ctal/Douyin_TikTok_Download_API
- https://github.com/Evil0ctal/Douyin_TikTok_Download_API/blob/V4.1.2/crawlers/douyin/web/utils.py
