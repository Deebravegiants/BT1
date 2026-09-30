# [M] Xmlsoft Libxml2 v2.11.0 was discovered to contain an out-of-bounds read via the...

## Summary
Severity: Medium
Advisory: JLSEC-2025-81
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-81
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=2.11.5+0 <2.12.0+0

## Details
Xmlsoft Libxml2 v2.11.0 was discovered to contain an out-of-bounds read via the xmlSAX2StartElement() function at `/libxml2/SAX2.c`. This vulnerability allows attackers to cause a Denial of Service (DoS) via supplying a crafted XML file. NOTE: the vendor's position is that the product does not support the legacy SAX1 interface with custom callbacks; there is a crash even without crafted input.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/535
- https://lists.debian.org/debian-lts-announce/2025/02/msg00028.html
