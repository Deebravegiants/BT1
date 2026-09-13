# [M] Netty vulnerable to HTTP request smuggling and RTSP request injection via DefaultHttpRequest.setUri()

## Summary
Severity: Medium
Advisory: CVE-2026-41417
Aliases: GHSA-v8h7-rr48-vmmv
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-41417
Type: osv

## Details
Netty allows request-line validation to be bypassed when a `DefaultHttpRequest` or `DefaultFullHttpRequest` is created first and its URI is later changed via `setUri()`. The constructors reject CRLF and whitespace characters that would break the start-line, but `setUri()` does not apply the same validation. `HttpRequestEncoder` and `RtspEncoder` then write the URI into the request line verbatim. If attacker-controlled input reaches `setUri()`, this enables CRLF injection and insertion of additional HTTP or RTSP requests, leading to HTTP request smuggling or desynchronization on the HTTP side and request injection on the RTSP side. This issue is fixed in versions 4.2.13.Final and 4.1.133.Final.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41417.json
- https://github.com/netty/netty/security/advisories/GHSA-v8h7-rr48-vmmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41417
