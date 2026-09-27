# [H] An issue was discovered in xmllint (from libxml2) before 2.11.8 and 2.12.x before 2.12.7

## Summary
Severity: High
Advisory: JLSEC-2025-84
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-84
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.12.7+0

## Details
An issue was discovered in xmllint (from libxml2) before 2.11.8 and 2.12.x before 2.12.7. Formatting error messages with xmllint --htmlout can result in a buffer over-read in xmlHTMLPrintFileContext in xmllint.c.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/720
- https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.11.8
- https://gitlab.gnome.org/GNOME/libxml2/-/releases/v2.12.7
- https://lists.debian.org/debian-lts-announce/2025/07/msg00014.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5HVUXKYTBWT3G5DEEQX62STJQBY367NL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/INKSSLW5VMZIXHRPZBAW4TJUX5SQKARG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VRDJCNQP32LV56KESUQ5SNZKAJWSZZRI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5HVUXKYTBWT3G5DEEQX62STJQBY367NL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/INKSSLW5VMZIXHRPZBAW4TJUX5SQKARG/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VRDJCNQP32LV56KESUQ5SNZKAJWSZZRI/
