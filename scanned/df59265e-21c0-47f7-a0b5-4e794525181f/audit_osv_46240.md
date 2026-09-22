# [M] JLSEC-2026-860

## Summary
Severity: Medium
Advisory: JLSEC-2026-860
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-860
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
A flaw was found in ImageMagick in `coders/hdr.c`. An attacker who submits a crafted file that is processed by ImageMagick could trigger undefined behavior in the form of values outside the range of type `unsigned char`. This would most likely lead to an impact to application availability, but could potentially cause other problems related to undefined behavior. This flaw affects ImageMagick versions prior to ImageMagick 7.0.8-68.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894680
- https://bugzilla.redhat.com/show_bug.cgi?id=1894680
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
