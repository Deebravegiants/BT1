# [H] JLSEC-2026-150

## Summary
Severity: High
Advisory: JLSEC-2026-150
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-150
Type: osv

## Affected
- Julia: `libexif_jll` — affected >=0 <0.6.26+0

## Details
libexif through 0.6.25 has a flaw in decoding MakerNotes. If the `exif_mnote_data_get_value` function gets passed in a 0 size, the passed in-buffer would be overwritten due to an integer underflow.

## References
- https://github.com/libexif/libexif/commit/7df372e9d31d7c993a22b913c813a5f7ec4f3692
- https://github.com/libexif/libexif/issues/247
