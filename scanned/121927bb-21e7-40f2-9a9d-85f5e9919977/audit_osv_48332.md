# [M] CVE-2017-6961

## Summary
Severity: Medium
Advisory: CVE-2017-6961
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-17
Source: https://osv.dev/vulnerability/CVE-2017-6961
Type: osv

## Details
An issue was discovered in apng2gif 1.7. There is improper sanitization of user input causing huge memory allocations, resulting in a crash. This is related to the read_chunk function using the pChunk->size value (within the PNG file) to determine the amount of memory to allocate.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=854441
