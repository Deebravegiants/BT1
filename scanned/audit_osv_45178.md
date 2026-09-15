# [H] A flaw was found in GLib

## Summary
Severity: High
Advisory: JLSEC-2025-163
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-163
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.76.5+0

## Details
A flaw was found in GLib. The GVariant deserialization code is vulnerable to a heap buffer overflow introduced by the fix for CVE-2023-32665. This bug does not affect any released version of GLib, but does affect GLib distributors who followed the guidance of GLib developers to backport the initial fix for CVE-2023-32665.

## References
- https://gitlab.gnome.org/GNOME/glib/-/issues/2840
- https://https://discourse.gnome.org/t/multiple-fixes-for-gvariant-normalisation-issues-in-glib/12835
- https://security.netapp.com/advisory/ntap-20240426-0005/
