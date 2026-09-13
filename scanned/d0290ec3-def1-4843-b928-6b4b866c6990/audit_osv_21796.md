# [M] CVE-2021-46534

## Summary
Severity: Medium
Advisory: CVE-2021-46534
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-27
Source: https://osv.dev/vulnerability/CVE-2021-46534
Type: osv

## Details
Cesanta MJS v2.20.0 was discovered to contain a SEGV vulnerability via getprop_builtin_foreign at src/mjs_exec.c. This vulnerability can lead to a Denial of Service (DoS).

## References
- https://github.com/cesanta/mjs/issues/204
