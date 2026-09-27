# [H] libxml2 before 2.12.10 and 2.13.x before 2.13.6 has a stack-based buffer overflow in...

## Summary
Severity: High
Advisory: JLSEC-2025-87
Ecosystem: Julia
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-87
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.13.6+1

## Details
libxml2 before 2.12.10 and 2.13.x before 2.13.6 has a stack-based buffer overflow in xmlSnprintfElements in valid.c. To exploit this, DTD validation must occur for an untrusted document or untrusted DTD. NOTE: this is similar to CVE-2017-9047.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/847
- https://issues.oss-fuzz.com/issues/392687022
- https://lists.debian.org/debian-lts-announce/2025/02/msg00028.html
- https://security.netapp.com/advisory/ntap-20250321-0006/
