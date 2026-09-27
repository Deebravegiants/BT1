# [H] A flaw was found in GLib

## Summary
Severity: High
Advisory: JLSEC-2025-168
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-168
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.84.3+0

## Details
A flaw was found in GLib. A denial of service on Windows platforms may occur if an application attempts to spawn a program using long command lines.

## References
- https://access.redhat.com/security/cve/CVE-2025-4056
- https://bugzilla.redhat.com/show_bug.cgi?id=2362826
- https://gitlab.gnome.org/GNOME/glib/-/issues/3668
