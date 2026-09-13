# [C] CVE-2021-27421

## Summary
Severity: Critical
Advisory: CVE-2021-27421
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-03
Source: https://osv.dev/vulnerability/CVE-2021-27421
Type: osv

## Details
NXP MCUXpresso SDK versions prior to 2.8.2 are vulnerable to integer overflow in SDK_Malloc function, which could allow to access memory locations outside the bounds of a specified array, leading to unexpected behavior such segmentation fault when assigning a particular block of memory from the heap via malloc.

## References
- https://mcuxpresso.nxp.com/en/welcome
- https://www.cisa.gov/uscert/ics/advisories/icsa-21-119-04
