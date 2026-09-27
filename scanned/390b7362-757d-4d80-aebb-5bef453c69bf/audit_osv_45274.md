# [M] LibTIFF 4.4.0 has an out-of-bounds read in tiffcrop in `tools/tiffcrop.c:3488`, allowing attackers...

## Summary
Severity: Medium
Advisory: JLSEC-2025-290
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-290
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
LibTIFF 4.4.0 has an out-of-bounds read in tiffcrop in `tools/tiffcrop.c:3488`, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit afaabc3e.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0795.json
- https://gitlab.com/libtiff/libtiff/-/commit/afaabc3e50d4e5d80a94143f7e3c997e7e410f68
- https://gitlab.com/libtiff/libtiff/-/issues/493
- https://lists.debian.org/debian-lts-announce/2023/02/msg00026.html
- https://security.gentoo.org/glsa/202305-31
- https://security.netapp.com/advisory/ntap-20230316-0003/
- https://www.debian.org/security/2023/dsa-5361
