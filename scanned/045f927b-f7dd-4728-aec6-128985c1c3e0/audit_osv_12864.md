# [M] CVE-2018-15853

## Summary
Severity: Medium
Advisory: CVE-2018-15853
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/CVE-2018-15853
Type: osv

## Details
Endless recursion exists in xkbcomp/expr.c in xkbcommon and libxkbcommon before 0.8.1, which could be used by local attackers to crash xkbcommon users by supplying a crafted keymap file that triggers boolean negation.

## References
- https://access.redhat.com/errata/RHSA-2019:2079
- https://security.gentoo.org/glsa/201810-05
- https://usn.ubuntu.com/3786-1/
- https://usn.ubuntu.com/3786-2/
- https://github.com/xkbcommon/libxkbcommon/commit/1f9d1248c07cda8aaff762429c0dce146de8632a
- https://lists.freedesktop.org/archives/wayland-devel/2018-August/039232.html
