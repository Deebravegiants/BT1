# [H] ESF-IDF: Remote Null Pointer Dereference in WebSocket Server

## Summary
Severity: High
Advisory: CVE-2026-45541
Aliases: GHSA-3j8v-xgrq-5vg8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45541
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. In versions 5.2.6, 5.3.5, 5.4.4, 5.5.4, and 6.0, a NULL-pointer dereference exists in the WebSocket subprotocol-negotiation path of the esp_http_server component. While parsing the client-supplied Sec-WebSocket-Protocol request header during the WebSocket handshake, the tokenisation result is dereferenced without a NULL check, so a malformed header value can crash the server before any application-level authentication runs. This issue has been patched in versions 5.2.7, 5.3.6, 5.4.5, 5.5.5, and 6.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45541.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-3j8v-xgrq-5vg8
- https://nvd.nist.gov/vuln/detail/CVE-2026-45541
- https://github.com/espressif/esp-idf/commit/00a2f7fbbbd8fe6d04729022e1d5c9a49435bfe8
- https://github.com/espressif/esp-idf/commit/0dc4ee7537f3b12350f5966cecacd59bba840ec6
- https://github.com/espressif/esp-idf/commit/37508ab91124ef426a7396d30f79eba1162700c7
- https://github.com/espressif/esp-idf/commit/9fc0ca13b3b85b98d32b98cd9dc8ff9d82642b7b
- https://github.com/espressif/esp-idf/commit/dc46dc51359749e50617eb70d6f9ae298adc4fff
- https://github.com/espressif/esp-idf/commit/f88a47e4f37fb11ae4b0908cd5c80059d83198c6
