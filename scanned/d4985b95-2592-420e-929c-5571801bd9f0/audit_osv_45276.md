# [M] LibTIFF 4.4.0 has an out-of-bounds write in tiffcrop in `tools/tiffcrop.c:3502`, allowing attackers...

## Summary
Severity: Medium
Advisory: JLSEC-2025-295
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-295
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
LibTIFF 4.4.0 has an out-of-bounds write in tiffcrop in `tools/tiffcrop.c:3502`, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 33aee127.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0800.json
- https://gitlab.com/libtiff/libtiff/-/commit/33aee1275d9d1384791d2206776eb8152d397f00
- https://gitlab.com/libtiff/libtiff/-/issues/496
- https://lists.debian.org/debian-lts-announce/2023/02/msg00026.html
- https://security.gentoo.org/glsa/202305-31
- https://security.netapp.com/advisory/ntap-20230316-0002/
- https://www.debian.org/security/2023/dsa-5361
