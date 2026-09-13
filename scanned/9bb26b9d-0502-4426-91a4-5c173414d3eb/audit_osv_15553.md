# [H] CVE-2019-17178

## Summary
Severity: High
Advisory: CVE-2019-17178
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-04
Source: https://osv.dev/vulnerability/CVE-2019-17178
Type: osv

## Details
HuffmanTree_makeFromFrequencies in lodepng.c in LodePNG through 2019-09-28, as used in WinPR in FreeRDP and other products, has a memory leak because a supplied realloc pointer (i.e., the first argument to realloc) is also used for a realloc return value.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00005.html
- https://github.com/FreeRDP/FreeRDP/issues/5645
- https://github.com/FreeRDP/FreeRDP/commit/9fee4ae076b1ec97b97efb79ece08d1dab4df29a
