# [C] CVE-2020-15471

## Summary
Severity: Critical
Advisory: CVE-2020-15471
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-07-01
Source: https://osv.dev/vulnerability/CVE-2020-15471
Type: osv

## Details
In nDPI through 3.2, the packet parsing code is vulnerable to a heap-based buffer over-read in ndpi_parse_packet_line_info in lib/ndpi_main.c.

## References
- https://github.com/fuzzing2026/CVE-PoCs/tree/main/ndpi-CVE-2020-15471
- https://github.com/ntop/nDPI/commit/61066fb106efa6d3d95b67e47b662de208b2b622
