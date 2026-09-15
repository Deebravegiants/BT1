# [M] A stack overflow was discovered in the `_TIFFVGetField` function of Tiffsplit v4.4.0

## Summary
Severity: Medium
Advisory: JLSEC-2025-275
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-275
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=4.4.0+0 <4.5.1+0

## Details
A stack overflow was discovered in the `_TIFFVGetField` function of Tiffsplit v4.4.0. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted TIFF file parsed by the "tiffsplit" or "tiffcrop" utilities.

## References
- https://gitlab.com/libtiff/libtiff/-/issues/433
- https://gitlab.com/libtiff/libtiff/-/issues/486
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FC6LWPAEKYJ57LSHX4SBFMLRMLOZTHIJ/
- https://security.netapp.com/advisory/ntap-20220930-0002/
- https://www.debian.org/security/2023/dsa-5333
