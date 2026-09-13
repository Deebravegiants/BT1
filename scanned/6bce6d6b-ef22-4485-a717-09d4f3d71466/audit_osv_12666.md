# [H] CVE-2018-14072

## Summary
Severity: High
Advisory: CVE-2018-14072
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-15
Source: https://osv.dev/vulnerability/CVE-2018-14072
Type: osv

## Details
libsixel 1.8.1 has a memory leak in sixel_decoder_decode in decoder.c, image_buffer_resize in fromsixel.c, and sixel_decode_raw in fromsixel.c.

## References
- https://github.com/saitoha/libsixel/issues/67#issue-341198610
