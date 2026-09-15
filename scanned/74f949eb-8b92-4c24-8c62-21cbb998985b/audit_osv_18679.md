# [M] CVE-2020-35357

## Summary
Severity: Medium
Advisory: CVE-2020-35357
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-35357
Type: osv

## Details
A buffer overflow can occur when calculating the quantile value using the Statistics Library of GSL (GNU Scientific Library), versions 2.5 and 2.6. Processing a maliciously crafted input data for gsl_stats_quantile_from_sorted_data of the library may lead to unexpected application termination or arbitrary code execution.

## References
- https://lists.debian.org/debian-lts-announce/2024/12/msg00006.html
- https://lists.debian.org/debian-lts-announce/2023/09/msg00023.html
- https://git.savannah.gnu.org/cgit/gsl.git/commit/?id=989a193268b963aa1047814f7f1402084fb7d859
- https://savannah.gnu.org/bugs/?59624
