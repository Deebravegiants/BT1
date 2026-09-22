# [C] CVE-2020-9760

## Summary
Severity: Critical
Advisory: CVE-2020-9760
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-23
Source: https://osv.dev/vulnerability/CVE-2020-9760
Type: osv

## Details
An issue was discovered in WeeChat before 2.7.1 (0.3.4 to 2.7 are affected). When a new IRC message 005 is received with longer nick prefixes, a buffer overflow and possibly a crash can happen when a new mode is set for a nick.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00031.html
- https://lists.debian.org/debian-lts-announce/2021/09/msg00018.html
- https://security.gentoo.org/glsa/202003-51
- https://weechat.org/doc/security/
- https://github.com/weechat/weechat/commit/40ccacb4330a64802b1f1e28ed9a6b6d3ca9197f
