# [H] CVE-2021-20309

## Summary
Severity: High
Advisory: CVE-2021-20309
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-11
Source: https://osv.dev/vulnerability/CVE-2021-20309
Type: osv

## Details
A flaw was found in ImageMagick in versions before 7.0.11 and before 6.9.12, where a division by zero in WaveImage() of MagickCore/visual-effects.c may trigger undefined behavior via a crafted image file submitted to an application using ImageMagick. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00000.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1946722
