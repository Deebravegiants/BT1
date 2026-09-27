# [M] JLSEC-2026-545

## Summary
Severity: Medium
Advisory: JLSEC-2026-545
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-545
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=2.4.0+0 <2.5.0+0

## Details
Integer Overflow in OpenJPEG v2.4.0 allows remote attackers to crash the application, causing a Denial of Service (DoS). This occurs when the attacker uses the command line option "-ImgDir" on a directory that contains 1048576 files.

## References
- https://github.com/uclouvain/openjpeg/issues/1338
- https://lists.debian.org/debian-lts-announce/2022/04/msg00006.html
- https://lists.debian.org/debian-lts-announce/2025/04/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZ54FGM2IGAP4AWSJ22JKHOPHCR3FGYU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QB6AI7CWXWMEDZIQY4LQ6DMIEXMDOHUP/
- https://security.gentoo.org/glsa/202209-04
