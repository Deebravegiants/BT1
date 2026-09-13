# [M] CVE-2021-46700

## Summary
Severity: Medium
Advisory: CVE-2021-46700
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-19
Source: https://osv.dev/vulnerability/CVE-2021-46700
Type: osv

## Details
In libsixel 1.8.6, sixel_encoder_output_without_macro (called from sixel_encoder_encode_frame in encoder.c) has a double free.

## References
- https://github.com/saitoha/libsixel/issues/158
