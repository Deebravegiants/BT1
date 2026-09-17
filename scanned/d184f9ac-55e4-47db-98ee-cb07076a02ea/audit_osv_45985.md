# [H] JLSEC-2026-543

## Summary
Severity: High
Advisory: JLSEC-2026-543
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-543
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=0 <2.4.0+0

## Details
OpenJPEG through 2.3.1 has a heap-based buffer overflow in `opj_t1_clbl_decode_processor` in `openjp2/t1.c` because of lack of `opj_j2k_update_image_dimensions` validation.

## References
- https://access.redhat.com/errata/RHSA-2020:0262
- https://access.redhat.com/errata/RHSA-2020:0274
- https://access.redhat.com/errata/RHSA-2020:0296
- https://github.com/uclouvain/openjpeg/issues/1228
- https://lists.debian.org/debian-lts-announce/2020/01/msg00025.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LACIIDDCKZJEPKTTFILSOSBQL7L3FC6V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XBRMI2D3XPVWKE3V52KRBW7BJVLS5LD3/
- https://www.debian.org/security/2021/dsa-4882
- https://www.oracle.com/security-alerts/cpujul2020.html
