# [M] CVE-2021-46546

## Summary
Severity: Medium
Advisory: CVE-2021-46546
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-27
Source: https://osv.dev/vulnerability/CVE-2021-46546
Type: osv

## Details
Cesanta MJS v2.20.0 was discovered to contain a SEGV vulnerability via mjs_next at src/mjs_object.c. This vulnerability can lead to a Denial of Service (DoS).

## References
- https://github.com/cesanta/mjs/issues/213
