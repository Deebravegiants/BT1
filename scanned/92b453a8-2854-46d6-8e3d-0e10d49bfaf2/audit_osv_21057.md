# [M] CVE-2021-4022

## Summary
Severity: Medium
Advisory: CVE-2021-4022
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-4022
Type: osv

## Details
A vulnerability was found in rizin. The bug involves an ELF64 binary for the HPPA architecture. When a specially crafted binarygets analysed by rizin, it causes rizin to crash by freeing an uninitialized (and potentially user controlled, depending on the build) memory address.

## References
- https://github.com/rizinorg/rizin/issues/2015
