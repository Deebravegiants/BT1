# [M] CVE-2018-11496

## Summary
Severity: Medium
Advisory: CVE-2018-11496
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-26
Source: https://osv.dev/vulnerability/CVE-2018-11496
Type: osv

## Details
In Long Range Zip (aka lrzip) 0.631, there is a use-after-free in read_stream in stream.c, because decompress_file in lrzip.c lacks certain size validation.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00001.html
- https://github.com/ckolivas/lrzip/issues/96
