# [H] CVE-2018-16985

## Summary
Severity: High
Advisory: CVE-2018-16985
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-13
Source: https://osv.dev/vulnerability/CVE-2018-16985
Type: osv

## Details
In Lizard (formerly LZ5) 2.0, use of an invalid memory address was discovered in LZ5_compress_continue in lz5_compress.c, related to LZ5_compress_fastSmall and MEM_read32. The vulnerability causes a segmentation fault and application crash, which leads to denial of service.

## References
- https://github.com/inikep/lizard/issues/18
