# [M] CVE-2021-34342

## Summary
Severity: Medium
Advisory: CVE-2021-34342
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-34342
Type: osv

## Details
Ming 0.4.8 has an out-of-bounds read vulnerability in the function newVar_N() in decompile.c which causes a huge information leak.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1969619
- https://github.com/libming/libming/issues/205
