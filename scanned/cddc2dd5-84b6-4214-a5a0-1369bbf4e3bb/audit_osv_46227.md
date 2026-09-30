# [M] JLSEC-2026-840

## Summary
Severity: Medium
Advisory: JLSEC-2026-840
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-840
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.0+0

## Details
A call to ConformPixelInfo() in the SetImageAlphaChannel() routine of `/MagickCore/channel.c` caused a subsequent heap-use-after-free or heap-buffer-overflow READ when GetPixelRed() or GetPixelBlue() was called. This could occur if an attacker is able to submit a malicious image file to be processed by ImageMagick and could lead to denial of service. It likely would not lead to anything further because the memory is used as pixel data and not e.g. a function pointer. This flaw affects ImageMagick versions prior to 7.0.9-0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1891601
- https://bugzilla.redhat.com/show_bug.cgi?id=1891601
- https://github.com/ImageMagick/ImageMagick/issues/1723
- https://github.com/ImageMagick/ImageMagick/issues/1723
- https://github.com/ImageMagick/ImageMagick/issues/1723#issuecomment-718275153
- https://github.com/ImageMagick/ImageMagick/issues/1723#issuecomment-718275153
