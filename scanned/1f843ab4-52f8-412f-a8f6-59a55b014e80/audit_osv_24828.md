# [M] CVE-2023-2731

## Summary
Severity: Medium
Advisory: CVE-2023-2731
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-17
Source: https://osv.dev/vulnerability/CVE-2023-2731
Type: osv

## Details
A NULL pointer dereference flaw was found in Libtiff's LZWDecode() function in the libtiff/tif_lzw.c file. This flaw allows a local attacker to craft specific input data that can cause the program to dereference a NULL pointer when decompressing a TIFF format file, resulting in a program crash or denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-2731
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2731.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2731
- https://security.netapp.com/advisory/ntap-20230703-0009/
- https://bugzilla.redhat.com/show_bug.cgi?id=2207635
- https://gitlab.com/libtiff/libtiff/-/issues/548
- https://github.com/libsdl-org/libtiff/commit/9be22b639ea69e102d3847dca4c53ef025e9527b
