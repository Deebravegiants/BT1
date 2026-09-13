# [H] JLSEC-2026-827

## Summary
Severity: High
Advisory: JLSEC-2026-827
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-827
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
ImageMagick before 7.0.8-50 has a "use of uninitialized value" vulnerability in the function ReadCUTImage in `coders/cut.c`.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://github.com/ImageMagick/ImageMagick/commit/cdb383749ef7b68a38891440af8cc23e0115306d
- https://github.com/ImageMagick/ImageMagick/commit/cdb383749ef7b68a38891440af8cc23e0115306d
- https://github.com/ImageMagick/ImageMagick/issues/1599
- https://github.com/ImageMagick/ImageMagick/issues/1599
- https://github.com/ImageMagick/ImageMagick6/commit/1e59b29e520d2beab73e8c78aacd5f1c0d76196d
- https://github.com/ImageMagick/ImageMagick6/commit/1e59b29e520d2beab73e8c78aacd5f1c0d76196d
- https://lists.debian.org/debian-lts-announce/2019/08/msg00021.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://support.f5.com/csp/article/K20336394
- https://support.f5.com/csp/article/K20336394
- https://support.f5.com/csp/article/K20336394?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.f5.com/csp/article/K20336394?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4192-1/
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://www.debian.org/security/2020/dsa-4712
