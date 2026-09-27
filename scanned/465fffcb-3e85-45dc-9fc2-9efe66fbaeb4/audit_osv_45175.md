# [H] A flaw was found in GLib

## Summary
Severity: High
Advisory: JLSEC-2025-160
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-160
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.76.5+0

## Details
A flaw was found in GLib. GVariant deserialization fails to validate that the input conforms to the expected format, leading to denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-29499
- https://bugzilla.redhat.com/show_bug.cgi?id=2211828
- https://gitlab.gnome.org/GNOME/glib/-/issues/2794
- https://lists.debian.org/debian-lts-announce/2023/09/msg00030.html
- https://security.gentoo.org/glsa/202311-18
- https://security.netapp.com/advisory/ntap-20231103-0001/
