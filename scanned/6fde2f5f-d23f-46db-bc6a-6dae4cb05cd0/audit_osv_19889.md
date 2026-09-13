# [M] CVE-2021-27347

## Summary
Severity: Medium
Advisory: CVE-2021-27347
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/CVE-2021-27347
Type: osv

## Details
Use after free in lzma_decompress_buf function in stream.c in Irzip 0.631 allows attackers to cause Denial of Service (DoS) via a crafted compressed file.

## References
- https://lists.debian.org/debian-lts-announce/2022/04/msg00012.html
- https://github.com/ckolivas/lrzip/issues/165
