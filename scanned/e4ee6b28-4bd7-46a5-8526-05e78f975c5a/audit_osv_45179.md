# [M] A flaw was found in GLib

## Summary
Severity: Medium
Advisory: JLSEC-2025-164
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-164
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.76.5+0

## Details
A flaw was found in GLib. GVariant deserialization is vulnerable to an exponential blowup issue where a crafted GVariant can cause excessive processing, leading to denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-32665
- https://bugzilla.redhat.com/show_bug.cgi?id=2211827
- https://gitlab.gnome.org/GNOME/glib/-/issues/2121
- https://lists.debian.org/debian-lts-announce/2023/09/msg00030.html
- https://security.gentoo.org/glsa/202311-18
- https://security.netapp.com/advisory/ntap-20240426-0006/
