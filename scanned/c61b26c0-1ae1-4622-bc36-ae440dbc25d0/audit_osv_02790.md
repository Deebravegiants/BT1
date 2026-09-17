# [C] ALPINE-CVE-2023-25139

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-25139
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-25139
Type: osv

## Affected
- Alpine:v3.19: `mpfr4` — affected >=0 <4.2.1-r0
- Alpine:v3.20: `mpfr4` — affected >=0 <4.2.1-r0
- Alpine:v3.21: `mpfr4` — affected >=0 <4.2.1-r0
- Alpine:v3.22: `mpfr4` — affected >=0 <4.2.1-r0
- Alpine:v3.23: `mpfr4` — affected >=0 <4.2.1-r0
- Alpine:v3.24: `mpfr4` — affected >=0 <4.2.1-r0

## Details
sprintf in the GNU C Library (glibc) 2.37 has a buffer overflow (out-of-bounds write) in some situations with a correct buffer size. This is unrelated to CWE-676. It may write beyond the bounds of the destination buffer when attempting to write a padded, thousands-separated string representation of a number, if the buffer is allocated the exact size required to represent that number as a string. For example, 1,234,567 (with padding to 13) overflows by two bytes.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-25139
