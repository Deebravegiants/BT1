# [M] CVE-2021-46510

## Summary
Severity: Medium
Advisory: CVE-2021-46510
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-27
Source: https://osv.dev/vulnerability/CVE-2021-46510
Type: osv

## Details
There is an Assertion `s < mjs->owned_strings.buf + mjs->owned_strings.len' failed at src/mjs_gc.c in Cesanta MJS v2.20.0.

## References
- https://github.com/cesanta/mjs/issues/185
