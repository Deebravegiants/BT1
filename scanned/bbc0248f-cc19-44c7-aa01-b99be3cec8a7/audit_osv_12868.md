# [H] CVE-2018-15857

## Summary
Severity: High
Advisory: CVE-2018-15857
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/CVE-2018-15857
Type: osv

## Details
An invalid free in ExprAppendMultiKeysymList in xkbcomp/ast-build.c in xkbcommon before 0.8.1 could be used by local attackers to crash xkbcommon keymap parsers or possibly have unspecified other impact by supplying a crafted keymap file.

## References
- https://access.redhat.com/errata/RHSA-2019:2079
- https://security.gentoo.org/glsa/201810-05
- https://usn.ubuntu.com/3786-1/
- https://usn.ubuntu.com/3786-2/
- https://github.com/xkbcommon/libxkbcommon/commit/c1e5ac16e77a21f87bdf3bc4dea61b037a17dddb
- https://lists.freedesktop.org/archives/wayland-devel/2018-August/039232.html
