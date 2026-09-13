# [M] LibTIFF is vulnerable to an integer overflow

## Summary
Severity: Medium
Advisory: JLSEC-2025-312
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-312
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.6.0+0

## Details
LibTIFF is vulnerable to an integer overflow. This flaw allows remote attackers to cause a denial of service (application crash) or possibly execute an arbitrary code via a crafted tiff image, which triggers a heap-based buffer overflow.

## References
- https://access.redhat.com/errata/RHSA-2024:2289
- https://access.redhat.com/security/cve/CVE-2023-40745
- https://bugzilla.redhat.com/show_bug.cgi?id=2235265
- https://security.netapp.com/advisory/ntap-20231110-0005/
