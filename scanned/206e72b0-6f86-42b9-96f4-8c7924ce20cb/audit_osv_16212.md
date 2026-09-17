# [M] CVE-2019-3573

## Summary
Severity: Medium
Advisory: CVE-2019-3573
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-02
Source: https://osv.dev/vulnerability/CVE-2019-3573
Type: osv

## Details
In libsixel v1.8.2, there is an infinite loop in the function sixel_decode_raw_impl() in the file fromsixel.c, as demonstrated by sixel2png.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/libsixel
- https://github.com/saitoha/libsixel/issues/83
