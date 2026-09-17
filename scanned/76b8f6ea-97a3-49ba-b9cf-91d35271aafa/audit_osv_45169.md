# [C] `file_copy_fallback` in `gio/gfile.c` in GNOME GLib 2.15.0 through 2.61.1 does not properly restrict...

## Summary
Severity: Critical
Advisory: JLSEC-2025-153
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-153
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.68.1+0

## Details
`file_copy_fallback` in `gio/gfile.c` in GNOME GLib 2.15.0 through 2.61.1 does not properly restrict file permissions while a copy operation is in progress. Instead, default permissions are used.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00076.html
- https://access.redhat.com/errata/RHSA-2019:3530
- https://gitlab.gnome.org/GNOME/glib/commit/d8f8f4d637ce43f8699ba94c9b7648beda0ca174
- https://lists.debian.org/debian-lts-announce/2019/06/msg00013.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2W4WIOAGO3M743M5KZLVQZM3NGHQDYLI/
- https://security.netapp.com/advisory/ntap-20190606-0003/
- https://usn.ubuntu.com/4014-1/
- https://usn.ubuntu.com/4014-2/
