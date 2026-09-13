# [C] CVE-2017-18212

## Summary
Severity: Critical
Advisory: CVE-2017-18212
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-18212
Type: osv

## Details
An issue was discovered in JerryScript 1.0. There is a heap-based buffer over-read in the lit_read_code_unit_from_hex function in lit/lit-char-helpers.c via a RegExp("[\x0"); payload.

## References
- https://github.com/jerryscript-project/jerryscript/issues/2140
