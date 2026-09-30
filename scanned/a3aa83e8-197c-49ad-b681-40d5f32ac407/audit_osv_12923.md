# [H] CVE-2018-16376

## Summary
Severity: High
Advisory: CVE-2018-16376
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16376
Type: osv

## Details
An issue was discovered in OpenJPEG 2.3.0. A heap-based buffer overflow was discovered in the function t2_encode_packet in lib/openmj2/t2.c. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service or possibly unspecified other impact.

## References
- http://www.securityfocus.com/bid/105262
- https://github.com/uclouvain/openjpeg/issues/1127
