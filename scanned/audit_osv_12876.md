# [M] CVE-2018-15870

## Summary
Severity: Medium
Advisory: CVE-2018-15870
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/CVE-2018-15870
Type: osv

## Details
An invalid memory address dereference was discovered in decompileGETVARIABLE in libming 0.4.8 before 2018-03-12. The vulnerability causes a segmentation fault and application crash, which leads to denial of service.

## References
- https://github.com/libming/libming/issues/122
