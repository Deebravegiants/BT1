# [M] Memos has Cross-Site Scripting (XSS) Vulnerability in Image URLs

## Summary
Severity: Medium
Advisory: GHSA-hfcf-79gh-f3jc
CVE: CVE-2025-50738
CWE: CWE-200, CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N/E:P (CVSS_V4)
Published: 2025-07-29
Source: https://github.com/advisories/GHSA-hfcf-79gh-f3jc
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.24.4

## Details
The Memos application, up to version v0.24.3, allows for the embedding of markdown images with arbitrary URLs. When a user views a memo containing such an image, their browser automatically fetches the image URL without explicit user consent or interaction beyond viewing the memo. This can be exploited by an attacker to disclose the viewing user's IP address, browser User-Agent string, and potentially other request-specific information to the attacker-controlled server, leading to information disclosure and user tracking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-50738
- https://github.com/usememos/memos/issues/4707#issuecomment-2898504237
- https://github.com/usememos/memos/commit/46d5307d7f210067b46e07400a728fa9095803d9
- https://github.com/fai1424/Vulnerability-Research/tree/main/CVE-2025-50738
- https://github.com/usememos/memos
