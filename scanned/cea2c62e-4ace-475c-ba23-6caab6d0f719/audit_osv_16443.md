# [M] CVE-2019-6976

## Summary
Severity: Medium
Advisory: CVE-2019-6976
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-01-26
Source: https://osv.dev/vulnerability/CVE-2019-6976
Type: osv

## Details
libvips before 8.7.4 generates output images from uninitialized memory locations when processing corrupted input image data because iofuncs/memory.c does not zero out allocated memory. This can result in leaking raw process memory contents through the output image.

## References
- https://blog.silentsignal.eu/2019/04/18/drop-by-drop-bleeding-through-libvips/
- https://github.com/libvips/libvips/releases/tag/v8.7.4
- https://github.com/libvips/libvips/commit/00622428bda8d7521db8d74260b519fa41d69d0a
