# [M] WeeChat has a Decompression Bomb in Relay WebSocket (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-53524
Aliases: GHSA-v2v4-45wm-5cr3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-53524
Type: osv

## Details
WeeChat (Wee Enhanced Environment for Chat) is a free chat client. In versions 4.3.0 through 4.9.0, the WeeChat relay module's WebSocket permessage-deflate decompression function relay_websocket_inflate() has no upper bound on output size. An authenticated relay user can send a small compressed WebSocket frame (~100 bytes) that decompresses to gigabytes, exhausting all server memory and crashing the entire WeeChat process. The api protocol enables permessage-deflate and requires authentication before WebSocket upgrade. Version 4.9.1 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53524.json
- https://github.com/weechat/weechat/security/advisories/GHSA-v2v4-45wm-5cr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-53524
