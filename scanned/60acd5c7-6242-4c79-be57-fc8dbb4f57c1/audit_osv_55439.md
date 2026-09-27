# [M] CVE-2025-48188

## Summary
Severity: Medium
Advisory: CVE-2025-48188
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-48188
Type: osv

## Details
libpspp-core.a in GNU PSPP through 2.0.1 has an incorrect call from fill_buffer (in data/encrypted-file.c) to the Gnulib rijndaelDecrypt function, leading to a heap-based buffer over-read.

## References
- https://savannah.gnu.org/bugs/?67079
