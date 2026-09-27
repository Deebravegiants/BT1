# [H] CVE-2023-50671

## Summary
Severity: High
Advisory: CVE-2023-50671
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-11
Source: https://osv.dev/vulnerability/CVE-2023-50671
Type: osv

## Details
In exiftags 1.01, nikon_prop1 in nikon.c has a heap-based buffer overflow (write of size 28) because snprintf can write to an unexpected address.

## References
- https://johnst.org/sw/exiftags/
- https://blog.yulun.ac.cn/posts/2023/fuzzing-exiftags/
