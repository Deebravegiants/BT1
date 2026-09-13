# [C] CVE-2021-26461

## Summary
Severity: Critical
Advisory: CVE-2021-26461
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-21
Source: https://osv.dev/vulnerability/CVE-2021-26461
Type: osv

## Details
Apache Nuttx Versions prior to 10.1.0 are vulnerable to integer wrap-around in functions malloc, realloc and memalign. This improper memory assignment can lead to arbitrary memory allocation, resulting in unexpected behavior such as a crash or a remote code injection/execution.

## References
- https://lists.apache.org/thread.html/r806fccf8b003ae812d807c6c7d97950d44ed29b2713418cbe3f2bddd%40%3Cdev.nuttx.apache.org%3E
