# [M] CVE-2020-21677

## Summary
Severity: Medium
Advisory: CVE-2020-21677
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-10
Source: https://osv.dev/vulnerability/CVE-2020-21677
Type: osv

## Details
A heap-based buffer overflow in the sixel_encoder_output_without_macro function in encoder.c of Libsixel 1.8.4 allows attackers to cause a denial of service (DOS) via converting a crafted PNG file into Sixel format.

## References
- https://github.com/saitoha/libsixel/issues/123
