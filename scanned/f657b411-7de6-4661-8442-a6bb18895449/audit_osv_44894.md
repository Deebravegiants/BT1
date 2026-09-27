# [H] Open WebUI: SSRF into internal services via DNS rebinding in the Playwright web loader

## Summary
Severity: High
Advisory: CVE-2026-87996
Aliases: GHSA-4v28-j6q3-5m4r
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87996
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.9.6 until 0.11.1, SafePlaywrightURLLoader in backend/open_webui/retrieval/web/utils.py validated a user-controlled hostname in Python and then let the Playwright browser resolve it again in the sync and async request interceptors. An authenticated user controlling authoritative DNS could return a public address to validation and an internal address to the browser, exposing responses from internal services or cloud metadata through web search or URL ingestion. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87996.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-4v28-j6q3-5m4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-87996
- https://github.com/open-webui/open-webui/commit/27402ff210bfa253445720920dfb86b15a00327b
- https://github.com/open-webui/open-webui/pull/28634
