# [M] JLSEC-2026-482

## Summary
Severity: Medium
Advisory: JLSEC-2026-482
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-482
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.1.0+0

## Details
Buffer Overflow in LibTiff v4.0.10 allows attackers to cause a denial of service via the "TIFFVGetField" funtion in the component '`libtiff/tif_dir.c`'.

## References
- http://bugzilla.maptools.org/show_bug.cgi?id=2851
- https://gitlab.com/libtiff/libtiff/-/issues/158
- https://gitlab.com/libtiff/libtiff/-/merge_requests/119
- https://security.netapp.com/advisory/ntap-20211004-0005/
- https://www.debian.org/security/2021/dsa-4997
