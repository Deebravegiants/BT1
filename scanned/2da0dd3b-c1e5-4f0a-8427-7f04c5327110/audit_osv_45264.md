# [M] A heap buffer overflow flaw was found in Libtiffs' tiffinfo.c in TIFFReadRawDataStriped() function

## Summary
Severity: Medium
Advisory: JLSEC-2025-280
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-280
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.4.0+0

## Details
A heap buffer overflow flaw was found in Libtiffs' tiffinfo.c in TIFFReadRawDataStriped() function. This flaw allows an attacker to pass a crafted TIFF file to the tiffinfo tool, triggering a heap buffer overflow issue and causing a crash that leads to a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2022-1354
- https://bugzilla.redhat.com/show_bug.cgi?id=2074404
- https://gitlab.com/libtiff/libtiff/-/commit/87f580f39011109b3bb5f6eca13fac543a542798
- https://gitlab.com/libtiff/libtiff/-/issues/319
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20221014-0007/
- https://www.debian.org/security/2023/dsa-5333
