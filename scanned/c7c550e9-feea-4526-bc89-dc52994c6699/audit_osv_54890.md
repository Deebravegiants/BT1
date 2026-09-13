# [M] CVE-2024-57822

## Summary
Severity: Medium
Advisory: CVE-2024-57822
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-10
Source: https://osv.dev/vulnerability/CVE-2024-57822
Type: osv

## Details
In Raptor RDF Syntax Library through 2.0.16, there is a heap-based buffer over-read when parsing triples with the nquads parser in raptor_ntriples_parse_term_internal().

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00023.html
- https://github.com/dajobe/raptor/issues/70
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1067896
- https://github.com/pedrib/PoC/blob/master/fuzzing/raptor-fuzz.md
