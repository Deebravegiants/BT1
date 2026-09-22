# [C] CVE-2021-27433

## Summary
Severity: Critical
Advisory: CVE-2021-27433
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-03
Source: https://osv.dev/vulnerability/CVE-2021-27433
Type: osv

## Details
ARM mbed-ualloc memory library version 1.3.0 is vulnerable to integer wrap-around in function mbed_krbs, which can lead to arbitrary memory allocation, resulting in unexpected behavior such as a crash or a remote code injection/execution.

## References
- https://www.cisa.gov/uscert/ics/advisories/icsa-21-119-04
- https://github.com/ARMmbed/mbed-os/pull/14408
