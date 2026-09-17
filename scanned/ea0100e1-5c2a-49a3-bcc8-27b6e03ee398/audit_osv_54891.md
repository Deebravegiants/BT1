# [M] CVE-2024-57823

## Summary
Severity: Medium
Advisory: CVE-2024-57823
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-10
Source: https://osv.dev/vulnerability/CVE-2024-57823
Type: osv

## Details
In Raptor RDF Syntax Library through 2.0.16, there is an integer underflow when normalizing a URI with the turtle parser in raptor_uri_normalize_path().

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00023.html
- https://github.com/dajobe/raptor/issues/70
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1067896
- https://github.com/pedrib/PoC/blob/master/fuzzing/raptor-fuzz.md
