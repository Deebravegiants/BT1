# [M] Null source pointer passed as an argument to memcpy() function within TIFFFetchStripThing() in...

## Summary
Severity: Medium
Advisory: JLSEC-2025-260
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-260
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.4.0+0

## Details
Null source pointer passed as an argument to memcpy() function within TIFFFetchStripThing() in `tif_dirread.c` in libtiff versions from 3.9.0 to 4.3.0 could lead to Denial of Service via crafted TIFF file. For users that compile libtiff from sources, the fix is available with commit eecb0712.

## References
- https://gitlab.com/freedesktop-sdk/mirrors/gitlab/libtiff/libtiff/-/commit/eecb0712f4c3a5b449f70c57988260a667ddbdef
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0561.json
- https://gitlab.com/libtiff/libtiff/-/issues/362
- https://lists.debian.org/debian-lts-announce/2022/03/msg00001.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DZEHZ35XVO2VBZ4HHCMM6J6TQIDSBQOM/
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220318-0001/
- https://www.debian.org/security/2022/dsa-5108
