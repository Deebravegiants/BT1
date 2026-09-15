# [M] JLSEC-2026-868

## Summary
Severity: Medium
Advisory: JLSEC-2026-868
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-868
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
Due to a missing check for 0 value of `replace_extent`, it is possible for offset `p` to overflow in SubstituteString(), causing potential impact to application availability. This could be triggered by a crafted input file that is processed by ImageMagick. This flaw affects ImageMagick versions prior to 7.0.8-68.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894691
- https://bugzilla.redhat.com/show_bug.cgi?id=1894691
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
