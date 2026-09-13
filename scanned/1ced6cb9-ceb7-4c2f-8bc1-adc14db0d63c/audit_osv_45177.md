# [H] A flaw was found in glib, where the gvariant deserialization code is vulnerable to a denial of...

## Summary
Severity: High
Advisory: JLSEC-2025-162
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-162
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.76.5+0

## Details
A flaw was found in glib, where the gvariant deserialization code is vulnerable to a denial of service introduced by additional input validation added to resolve CVE-2023-29499. The offset table validation may be very slow. This bug does not affect any released version of glib but does affect glib distributors who followed the guidance of glib developers to backport the initial fix for CVE-2023-29499.

## References
- https://gitlab.gnome.org/GNOME/glib/-/issues/2841
- https://https://discourse.gnome.org/t/multiple-fixes-for-gvariant-normalisation-issues-in-glib/12835
- https://security.netapp.com/advisory/ntap-20231110-0002/
