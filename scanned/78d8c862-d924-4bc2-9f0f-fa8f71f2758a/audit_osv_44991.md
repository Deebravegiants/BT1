# [H] Decompression Bomb Bypass via Negative max_length in Streaming API in urllib3

## Summary
Severity: High
Advisory: CVE-2026-9375
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-9375
Type: osv

## Details
urllib3 version 2.6.3 is vulnerable to a decompression bomb bypass in its streaming API (`preload_content=False`) when using Brotli support. The issue arises due to three independent code paths in `response.py` that bypass the `max_length` protection introduced in version 2.6.0 to mitigate CVE-2025-66471. Specifically, negative `max_length` values can be produced due to buffer arithmetic in `read()`, `flush_decoder` unconditionally overrides `max_length` to `-1`, and `_flush_decoder()` passes no limit at all, defaulting to unlimited decompression. This allows a malicious HTTP server to trigger an out-of-memory (OOM) condition by decompressing large payloads into memory, leading to a denial of service (DoS). The vulnerability affects urllib3 2.6.3 and Brotli 1.2.0 and impacts applications and libraries using `requests` or `urllib3` to stream content from untrusted sources.

## References
- https://huntr.com/bounties/ddd09eb9-b87d-4a43-84df-48837b1bbc23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9375.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9375
- https://github.com/urllib3/urllib3/commit/2bdcc44d1e163fb5cc48a8662425e35e15adfe6a
