# [H] CVE-2017-6960

## Summary
Severity: High
Advisory: CVE-2017-6960
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-17
Source: https://osv.dev/vulnerability/CVE-2017-6960
Type: osv

## Details
An issue was discovered in apng2gif 1.7. There is an integer overflow resulting in a heap-based buffer over-read, related to the load_apng function and the imagesize variable.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00039.html
- https://usn.ubuntu.com/4513-1/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=854367
