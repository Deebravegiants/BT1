# [M] CVE-2020-25663

## Summary
Severity: Medium
Advisory: CVE-2020-25663
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-25663
Type: osv

## Details
A call to ConformPixelInfo() in the SetImageAlphaChannel() routine of /MagickCore/channel.c caused a subsequent heap-use-after-free or heap-buffer-overflow READ when GetPixelRed() or GetPixelBlue() was called. This could occur if an attacker is able to submit a malicious image file to be processed by ImageMagick and could lead to denial of service. It likely would not lead to anything further because the memory is used as pixel data and not e.g. a function pointer. This flaw affects ImageMagick versions prior to 7.0.9-0.

## References
- https://github.com/ImageMagick/ImageMagick/issues/1723#issuecomment-718275153
- https://bugzilla.redhat.com/show_bug.cgi?id=1891601
- https://github.com/ImageMagick/ImageMagick/issues/1723
