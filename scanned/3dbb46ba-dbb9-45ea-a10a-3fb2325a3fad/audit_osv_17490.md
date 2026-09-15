# [H] CVE-2020-15476

## Summary
Severity: High
Advisory: CVE-2020-15476
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-01
Source: https://osv.dev/vulnerability/CVE-2020-15476
Type: osv

## Details
In nDPI through 3.2, the Oracle protocol dissector has a heap-based buffer over-read in ndpi_search_oracle in lib/protocols/oracle.c.

## References
- https://lists.debian.org/debian-lts-announce/2022/08/msg00016.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00052.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=21780
- https://github.com/ntop/nDPI/commit/b69177be2fbe01c2442239a61832c44e40136c05
