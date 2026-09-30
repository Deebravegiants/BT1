# [H] JLSEC-2026-850

## Summary
Severity: High
Advisory: JLSEC-2026-850
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-850
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
A flaw was found in ImageMagick in `MagickCore/quantum-private.h`. An attacker who submits a crafted file that is processed by ImageMagick could trigger a heap buffer overflow. This would most likely lead to an impact to application availability, but could potentially lead to an impact to data integrity as well. This flaw affects ImageMagick versions prior to 7.0.9-0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894226
- https://bugzilla.redhat.com/show_bug.cgi?id=1894226
