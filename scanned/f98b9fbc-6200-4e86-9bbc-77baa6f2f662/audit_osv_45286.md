# [M] A vulnerability was found in libtiff due to multiple potential integer overflows in raw2tiff.c

## Summary
Severity: Medium
Advisory: JLSEC-2025-313
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-313
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.6.0+0

## Details
A vulnerability was found in libtiff due to multiple potential integer overflows in raw2tiff.c. This flaw allows remote attackers to cause a denial of service or possibly execute an arbitrary code via a crafted tiff image, which triggers a heap-based buffer overflow.

## References
- https://access.redhat.com/errata/RHSA-2024:2289
- https://access.redhat.com/security/cve/CVE-2023-41175
- https://bugzilla.redhat.com/show_bug.cgi?id=2235264
