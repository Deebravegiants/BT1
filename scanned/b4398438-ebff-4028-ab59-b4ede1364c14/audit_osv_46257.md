# [H] JLSEC-2026-888

## Summary
Severity: High
Advisory: JLSEC-2026-888
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-888
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
A flaw was found in ImageMagick in versions before 7.0.11. A potential cipher leak when the calculate signatures in TransformSignature is possible. The highest threat from this vulnerability is to data confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1947019
- https://bugzilla.redhat.com/show_bug.cgi?id=1947019
- https://lists.debian.org/debian-lts-announce/2021/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
