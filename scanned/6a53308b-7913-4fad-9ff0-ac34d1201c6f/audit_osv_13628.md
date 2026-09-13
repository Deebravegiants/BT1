# [M] CVE-2018-20591

## Summary
Severity: Medium
Advisory: CVE-2018-20591
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-30
Source: https://osv.dev/vulnerability/CVE-2018-20591
Type: osv

## Details
A heap-based buffer over-read was discovered in decompileJUMP function in util/decompile.c of libming v0.4.8. A crafted input can cause segmentation faults, leading to denial-of-service, as demonstrated by swftocxx.

## References
- https://github.com/libming/libming/issues/168
