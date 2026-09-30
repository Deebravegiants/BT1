# [M] CVE-2022-24130

## Summary
Severity: Medium
Advisory: CVE-2022-24130
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-31
Source: https://osv.dev/vulnerability/CVE-2022-24130
Type: osv

## Details
xterm through Patch 370, when Sixel support is enabled, allows attackers to trigger a buffer overflow in set_sixel in graphics_sixel.c via crafted text.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BP5Y4O7WBNLV24D22E6LE7RQFYOUVD2U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4CWYYEBT6AJRJBBQU2KLUOQDHRM7WAV/
- https://security.gentoo.org/glsa/202208-22
- https://lists.debian.org/debian-lts-announce/2022/02/msg00007.html
- https://invisible-island.net/xterm/xterm.log.html
- https://twitter.com/nickblack/status/1487731459398025216
- https://www.openwall.com/lists/oss-security/2022/01/30/2
- https://www.openwall.com/lists/oss-security/2022/01/30/3
