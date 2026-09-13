# [C] CVE-2022-45063

## Summary
Severity: Critical
Advisory: CVE-2022-45063
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-10
Source: https://osv.dev/vulnerability/CVE-2022-45063
Type: osv

## Details
xterm before 375 allows code execution via font ops, e.g., because an OSC 50 response may have Ctrl-g and therefore lead to command execution within the vi line-editing mode of Zsh. NOTE: font ops are not allowed in the xterm default configurations of some Linux distributions.

## References
- http://www.openwall.com/lists/oss-security/2024/06/15/1
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4TPVNTYFFWNTGZJJQAA4MGGFSTXA4XEA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5T2JI5JCHPTXX2KJU45H2XAHQSFVEJ2Y/
- http://www.openwall.com/lists/oss-security/2024/06/17/1
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IVD3I2ZFXGOY6BA2FNS7WPFMPFBDHFWC/
- https://invisible-island.net/xterm/xterm.log.html
- https://security.gentoo.org/glsa/202211-09
- https://news.ycombinator.com/item?id=33546415
- http://www.openwall.com/lists/oss-security/2022/11/10/1
- http://www.openwall.com/lists/oss-security/2022/11/10/5
- https://www.openwall.com/lists/oss-security/2022/11/10/1
