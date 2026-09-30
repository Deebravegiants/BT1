# [M] A flaw was found in libtiff

## Summary
Severity: Medium
Advisory: JLSEC-2025-308
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-308
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
A flaw was found in libtiff. A specially crafted tiff file can lead to a segmentation fault due to a buffer overflow in the Fax3Encode function in `libtiff/tif_fax3.c`, resulting in a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-3618
- https://bugzilla.redhat.com/show_bug.cgi?id=2215865
- https://lists.debian.org/debian-lts-announce/2023/07/msg00034.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00019.html
- https://security.netapp.com/advisory/ntap-20230824-0012/
- https://support.apple.com/kb/HT214036
- https://support.apple.com/kb/HT214037
- https://support.apple.com/kb/HT214038
