# [M] CVE-2020-19143

## Summary
Severity: Medium
Advisory: CVE-2020-19143
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-09
Source: https://osv.dev/vulnerability/CVE-2020-19143
Type: osv

## Details
Buffer Overflow in LibTiff v4.0.10 allows attackers to cause a denial of service via the "TIFFVGetField" funtion in the component 'libtiff/tif_dir.c'.

## References
- https://security.netapp.com/advisory/ntap-20211004-0005/
- https://www.debian.org/security/2021/dsa-4997
- http://bugzilla.maptools.org/show_bug.cgi?id=2851
- https://gitlab.com/libtiff/libtiff/-/issues/158
- https://gitlab.com/libtiff/libtiff/-/merge_requests/119
