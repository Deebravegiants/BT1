# [C] CVE-2019-19638

## Summary
Severity: Critical
Advisory: CVE-2019-19638
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-08
Source: https://osv.dev/vulnerability/CVE-2019-19638
Type: osv

## Details
An issue was discovered in libsixel 1.8.2. There is a heap-based buffer overflow in the function load_pnm at frompnm.c, due to an integer overflow.

## References
- https://github.com/saitoha/libsixel/issues/102
