# [M] CVE-2018-15855

## Summary
Severity: Medium
Advisory: CVE-2018-15855
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/CVE-2018-15855
Type: osv

## Details
Unchecked NULL pointer usage in xkbcommon before 0.8.1 could be used by local attackers to crash (NULL pointer dereference) the xkbcommon parser by supplying a crafted keymap file, because the XkbFile for an xkb_geometry section was mishandled.

## References
- https://access.redhat.com/errata/RHSA-2019:2079
- https://lists.freedesktop.org/archives/wayland-devel/2018-August/039232.html
- https://security.gentoo.org/glsa/201810-05
- https://usn.ubuntu.com/3786-1/
- https://usn.ubuntu.com/3786-2/
- https://github.com/xkbcommon/libxkbcommon/commit/917636b1d0d70205a13f89062b95e3a0fc31d4ff
