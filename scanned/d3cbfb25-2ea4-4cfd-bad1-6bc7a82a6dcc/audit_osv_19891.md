# [C] CVE-2021-27419

## Summary
Severity: Critical
Advisory: CVE-2021-27419
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-03
Source: https://osv.dev/vulnerability/CVE-2021-27419
Type: osv

## Details
uClibc-ng versions prior to 1.0.37 are vulnerable to integer wrap-around in functions malloc-simple. This improper memory assignment can lead to arbitrary memory allocation, resulting in unexpected behavior such as a crash or a remote code injection/execution.

## References
- https://downloads.uclibc-ng.org/releases/
- https://www.cisa.gov/uscert/ics/advisories/icsa-21-119-04
