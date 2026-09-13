# [M] CVE-2018-15858

## Summary
Severity: Medium
Advisory: CVE-2018-15858
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/CVE-2018-15858
Type: osv

## Details
Unchecked NULL pointer usage when handling invalid aliases in CopyKeyAliasesToKeymap in xkbcomp/keycodes.c in xkbcommon before 0.8.1 could be used by local attackers to crash (NULL pointer dereference) the xkbcommon parser by supplying a crafted keymap file.

## References
- https://security.gentoo.org/glsa/201810-05
- https://usn.ubuntu.com/3786-1/
- https://usn.ubuntu.com/3786-2/
- https://github.com/xkbcommon/libxkbcommon/commit/badb428e63387140720f22486b3acbd3d738859f
- https://lists.freedesktop.org/archives/wayland-devel/2018-August/039232.html
