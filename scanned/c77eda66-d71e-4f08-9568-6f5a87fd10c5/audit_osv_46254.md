# [H] JLSEC-2026-885

## Summary
Severity: High
Advisory: JLSEC-2026-885
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-885
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
A flaw was found in ImageMagick in versions before 7.0.11, where a division by zero ConvertXYZToJzazbz() of `MagickCore/colorspace.c` may trigger undefined behavior via a crafted image file that is submitted by an attacker and processed by an application using ImageMagick. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1946728
- https://bugzilla.redhat.com/show_bug.cgi?id=1946728
