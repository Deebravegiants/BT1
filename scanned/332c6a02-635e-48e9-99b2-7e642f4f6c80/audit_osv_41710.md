# [H] libevent evhttp: Multiple HTTP Parser Bugs Enable Request Smuggling

## Summary
Severity: High
Advisory: CVE-2026-63382
Aliases: GHSA-q39v-w2g7-gr8j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:L/SI:L/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63382
Type: osv

## Details
Libevent is an event notification library. Prior to 2.1.13 and 2.2.2-alpha, the libevent evhttp parser in http.c inconsistently handles duplicate Transfer-Encoding headers, comma-separated Transfer-Encoding values, and bare line feeds in chunked framing. evhttp_find_header can select only the first header, evhttp_check_transfer_encoding_ was absent so the previous whole-string comparison fails to recognize valid lists ending in chunked, and evhttp_handle_chunked_read uses EVBUFFER_EOL_CRLF rather than EVBUFFER_EOL_CRLF_STRICT, accepting bare LF chunk terminators. When libevent is deployed behind a proxy that frames the same request differently, an unauthenticated remote attacker can desynchronize request boundaries and smuggle a second request, potentially bypassing access controls or poisoning caches. This issue is fixed in versions 2.1.13 and 2.2.2-alpha.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.1.13-stable
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63382.json
- https://github.com/libevent/libevent/security/advisories/GHSA-q39v-w2g7-gr8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-63382
- https://github.com/libevent/libevent/commit/10abb34b8dc3e1184de315dd261ce4b77563cda6
- https://github.com/libevent/libevent/commit/5119ceb00557bf007f9065709e852686f3c0bb6e
- https://github.com/libevent/libevent/commit/83ba67373032334559b82409db035dd8c3cc1660
- https://github.com/libevent/libevent/commit/ac38703b2d312200c4f967f02936af0118d384a0
