# [H] CVE-2017-6962

## Summary
Severity: High
Advisory: CVE-2017-6962
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-17
Source: https://osv.dev/vulnerability/CVE-2017-6962
Type: osv

## Details
An issue was discovered in apng2gif 1.7. There is an integer overflow resulting in a heap-based buffer overflow. This is related to the read_chunk function making an unchecked addition of 12.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=854447
