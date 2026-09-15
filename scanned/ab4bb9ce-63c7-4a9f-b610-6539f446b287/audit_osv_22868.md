# [M] LibTIFF tif_getimage.c TIFFReadRGBATileExt integer overflow

## Summary
Severity: Medium
Advisory: CVE-2022-3970
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-11-13
Source: https://osv.dev/vulnerability/CVE-2022-3970
Type: osv

## Details
A vulnerability was found in LibTIFF. It has been classified as critical. This affects the function TIFFReadRGBATileExt of the file libtiff/tif_getimage.c. The manipulation leads to integer overflow. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. The name of the patch is 227500897dfb07fb7d27f7aa570050e62617e3be. It is recommended to apply a patch to fix this issue. The identifier VDB-213549 was assigned to this vulnerability.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=53137
- https://oss-fuzz.com/download?testcase_id=5738253143900160
- https://support.apple.com/kb/HT213841
- https://support.apple.com/kb/HT213843
- https://vuldb.com/?id.213549
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3970.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3970
- https://security.netapp.com/advisory/ntap-20221215-0009/
- https://gitlab.com/libtiff/libtiff/-/commit/227500897dfb07fb7d27f7aa570050e62617e3be
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
