# [C] CVE-2021-33797

## Summary
Severity: Critical
Advisory: CVE-2021-33797
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-17
Source: https://osv.dev/vulnerability/CVE-2021-33797
Type: osv

## Details
Buffer-overflow in jsdtoa.c in Artifex MuJS in versions 1.0.1 to 1.1.1. An integer overflow happens when js_strtod() reads in floating point exponent, which leads to a buffer overflow in the pointer *d.

## References
- https://github.com/ccxvii/mujs/issues/148
- https://github.com/ccxvii/mujs/commit/833b6f1672b4f2991a63c4d05318f0b84ef4d550
