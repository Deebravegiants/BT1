# [M] CVE-2018-15856

## Summary
Severity: Medium
Advisory: CVE-2018-15856
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/CVE-2018-15856
Type: osv

## Details
An infinite loop when reaching EOL unexpectedly in compose/parser.c (aka the keymap parser) in xkbcommon before 0.8.1 could be used by local attackers to cause a denial of service during parsing of crafted keymap files.

## References
- https://access.redhat.com/errata/RHSA-2019:2079
- https://security.gentoo.org/glsa/201810-05
- https://usn.ubuntu.com/3786-1/
- https://usn.ubuntu.com/3786-2/
- https://github.com/xkbcommon/libxkbcommon/commit/842e4351c2c97de6051cab6ce36b4a81e709a0e1
- https://lists.freedesktop.org/archives/wayland-devel/2018-August/039232.html
