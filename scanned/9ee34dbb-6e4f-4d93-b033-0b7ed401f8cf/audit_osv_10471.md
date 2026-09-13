# [H] CVE-2017-15924

## Summary
Severity: High
Advisory: CVE-2017-15924
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/CVE-2017-15924
Type: osv

## Details
In manager.c in ss-manager in shadowsocks-libev 3.1.0, improper parsing allows command injection via shell metacharacters in a JSON configuration request received via 127.0.0.1 UDP traffic, related to the add_server, build_config, and construct_command_line functions.

## References
- http://openwall.com/lists/oss-security/2017/10/13/2
- http://www.debian.org/security/2017/dsa-4009
- https://github.com/shadowsocks/shadowsocks-libev/commit/c67d275803dc6ea22c558d06b1f7ba9f94cd8de3
- https://github.com/shadowsocks/shadowsocks-libev/issues/1734
- https://www.x41-dsec.de/lab/advisories/x41-2017-010-shadowsocks-libev/
