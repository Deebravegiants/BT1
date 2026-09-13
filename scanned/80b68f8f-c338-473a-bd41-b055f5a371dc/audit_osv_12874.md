# [M] CVE-2018-15864

## Summary
Severity: Medium
Advisory: CVE-2018-15864
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/CVE-2018-15864
Type: osv

## Details
Unchecked NULL pointer usage in resolve_keysym in xkbcomp/parser.y in xkbcommon before 0.8.2 could be used by local attackers to crash (NULL pointer dereference) the xkbcommon parser by supplying a crafted keymap file, because a map access attempt can occur for a map that was never created.

## References
- https://access.redhat.com/errata/RHSA-2019:2079
- https://security.gentoo.org/glsa/201810-05
- https://usn.ubuntu.com/3786-1/
- https://usn.ubuntu.com/3786-2/
- https://github.com/xkbcommon/libxkbcommon/commit/a8ea7a1d3daa7bdcb877615ae0a252c189153bd2
- https://lists.freedesktop.org/archives/wayland-devel/2018-August/039243.html
