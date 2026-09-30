# [H] ffuf denial of service (OOM) via HTTP response decompression bomb

## Summary
Severity: High
Advisory: CVE-2026-73232
Aliases: GHSA-jcvh-xf52-2cwm, GO-2026-6369
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73232
Type: osv

## Details
ffuf is a fast web fuzzer written in Go. Prior to 2.2.0, ffuf allows a malicious target server to cause an out-of-memory denial of service because the response size guard in pkg/runner/simple.go checks only the compressed Content-Length while io.ReadAll reads gzip, brotli, deflate, transparently decompressed, or chunked response bodies without a decompressed-size bound. This issue is fixed in version 2.2.0.

## References
- https://github.com/ffuf/ffuf/releases/tag/v2.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73232.json
- https://github.com/ffuf/ffuf/security/advisories/GHSA-jcvh-xf52-2cwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-73232
- https://github.com/ffuf/ffuf/commit/fb0da86c60443b0dddbc9a86e91e3a6487dff79b
- https://github.com/ffuf/ffuf/pull/897
