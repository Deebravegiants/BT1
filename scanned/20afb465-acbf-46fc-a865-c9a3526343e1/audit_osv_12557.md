# [H] CVE-2018-12900

## Summary
Severity: High
Advisory: CVE-2018-12900
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-12900
Type: osv

## Details
Heap-based buffer overflow in the cpSeparateBufToContigBuf function in tiffcp.c in LibTIFF 3.9.3, 3.9.4, 3.9.5, 3.9.6, 3.9.7, 4.0.0beta7, 4.0.0alpha4, 4.0.0alpha5, 4.0.0alpha6, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.0.4, 4.0.4beta, 4.0.5, 4.0.6, 4.0.7, 4.0.8 and 4.0.9 allows remote attackers to cause a denial of service (crash) or possibly have unspecified other impact via a crafted TIFF file.

## References
- https://github.com/Hack-Me/Pocs_for_Multi_Versions/tree/main/CVE-2018-12900
- https://lists.debian.org/debian-lts-announce/2019/11/msg00027.html
- https://usn.ubuntu.com/3906-2/
- https://access.redhat.com/errata/RHSA-2019:2053
- https://access.redhat.com/errata/RHSA-2019:3419
- https://usn.ubuntu.com/3906-1/
- https://www.debian.org/security/2020/dsa-4670
- http://bugzilla.maptools.org/show_bug.cgi?id=2798
