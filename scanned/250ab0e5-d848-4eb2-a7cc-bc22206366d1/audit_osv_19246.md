# [C] CVE-2020-8955

## Summary
Severity: Critical
Advisory: CVE-2020-8955
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-8955
Type: osv

## Details
irc_mode_channel_update in plugins/irc/irc-mode.c in WeeChat through 2.7 allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a malformed IRC message 324 (channel mode).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ASRTCQFFDAAK347URWNDH6NSED2BGNY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ER23GT23US5JXDLUZAMGMWXKZ74MI4S2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M3LAJTLI3LWZRNCFYJ7PCBBTHUMCCBHH/
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00031.html
- https://lists.debian.org/debian-lts-announce/2021/09/msg00018.html
- https://security.gentoo.org/glsa/202003-51
- https://weechat.org/doc/security/
- https://github.com/weechat/weechat/commit/6f4f147d8e86adf9ad34a8ffd7e7f1f23a7e74da
