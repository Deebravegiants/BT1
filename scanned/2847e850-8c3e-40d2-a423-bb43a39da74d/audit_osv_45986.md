# [H] JLSEC-2026-544

## Summary
Severity: High
Advisory: JLSEC-2026-544
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-544
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=0 <2.4.0+0

## Details
`opj_t1_clbl_decode_processor` in `openjp2/t1.c` in OpenJPEG 2.3.1 through 2020-01-28 has a heap-based buffer overflow in the qmfbid==1 case, a different issue than CVE-2020-6851.

## References
- https://access.redhat.com/errata/RHSA-2020:0550
- https://access.redhat.com/errata/RHSA-2020:0569
- https://access.redhat.com/errata/RHSA-2020:0570
- https://access.redhat.com/errata/RHSA-2020:0694
- https://github.com/uclouvain/openjpeg/issues/1231
- https://lists.debian.org/debian-lts-announce/2020/01/msg00035.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EFM77GIFWHOECNIERYJQPI2ZJU57GZD5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TFEVEKETJV7GOXD5RDWL35ESEDHC663E/
- https://www.debian.org/security/2021/dsa-4882
- https://www.oracle.com/security-alerts/cpujul2020.html
