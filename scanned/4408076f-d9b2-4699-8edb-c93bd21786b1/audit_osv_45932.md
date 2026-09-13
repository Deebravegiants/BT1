# [M] JLSEC-2026-490

## Summary
Severity: Medium
Advisory: JLSEC-2026-490
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/JLSEC-2026-490
Type: osv

## Affected
- Julia: `LittleCMS_jll` — affected >=0 <2.12.0+0

## Details
Little CMS (aka Little Color Management System) 2.9 has an integer overflow in the AllocateDataSet function in cmscgats.c, leading to a heap-based buffer overflow in the SetData function via a crafted file in the second argument to cmsIT8LoadFromFile.

## References
- https://access.redhat.com/errata/RHSA-2018:3004
- https://github.com/mm2/Little-CMS/commit/768f70ca405cd3159d990e962d54456773bb8cf8
- https://github.com/mm2/Little-CMS/issues/171
- https://lists.debian.org/debian-lts-announce/2018/09/msg00005.html
- https://security.gentoo.org/glsa/202105-18
- https://usn.ubuntu.com/3770-1/
- https://usn.ubuntu.com/3770-2/
- https://www.debian.org/security/2018/dsa-4284
