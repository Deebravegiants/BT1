# [M] An issue was discovered in function TIFFReadDirectory libtiff before 4.4.0 allows attackers to cause...

## Summary
Severity: Medium
Advisory: JLSEC-2025-311
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-311
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.4.0+0

## Details
An issue was discovered in function TIFFReadDirectory libtiff before 4.4.0 allows attackers to cause a denial of service via crafted TIFF file.

## References
- https://gitlab.com/libtiff/libtiff/-/issues/455
- https://gitlab.com/libtiff/libtiff/-/merge_requests/386
