# [H] CVE-2021-40516

## Summary
Severity: High
Advisory: CVE-2021-40516
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-05
Source: https://osv.dev/vulnerability/CVE-2021-40516
Type: osv

## Details
WeeChat before 3.2.1 allows remote attackers to cause a denial of service (crash) via a crafted WebSocket frame that trigger an out-of-bounds read in plugins/relay/relay-websocket.c in the Relay plugin.

## References
- https://lists.debian.org/debian-lts-announce/2021/09/msg00018.html
- https://github.com/weechat/weechat/commit/8b1331f98de1714bae15a9ca2e2b393ba49d735b
- https://weechat.org/doc/security/
