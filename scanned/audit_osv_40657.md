# [H] LibreChat: SSRF via User-Provided Custom Endpoint baseURL — no private IP validation on user-configured API base URLs

## Summary
Severity: High
Advisory: CVE-2026-54033
Aliases: GHSA-gc9r-88c3-7qhq
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54033
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. Prior to 0.8.4-rc1, LibreChat allows users to configure custom OpenAI-compatible API endpoints by setting a baseURL. This URL is used to construct HTTP requests without any SSRF validation — no private IP check, no scheme restriction, no DNS pinning. An authenticated user can set baseURL to internal network addresses. This vulnerability is fixed in 0.8.4-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54033.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-gc9r-88c3-7qhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-54033
