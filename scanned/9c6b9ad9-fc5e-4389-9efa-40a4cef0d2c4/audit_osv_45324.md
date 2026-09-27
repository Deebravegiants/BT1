# [H] In libxml2 before 2.13.8 and 2.14.x before 2.14.2, out-of-bounds memory access can occur in the...

## Summary
Severity: High
Advisory: JLSEC-2025-89
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-89
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=2.14.1+0 <2.14.4+0

## Details
In libxml2 before 2.13.8 and 2.14.x before 2.14.2, out-of-bounds memory access can occur in the Python API (Python bindings) because of an incorrect return value. This occurs in xmlPythonFileRead and xmlPythonFileReadRaw because of a difference between bytes and characters.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/889
- https://lists.debian.org/debian-lts-announce/2025/04/msg00041.html
