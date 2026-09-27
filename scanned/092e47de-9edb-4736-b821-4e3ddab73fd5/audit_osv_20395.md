# [M] CVE-2021-33444

## Summary
Severity: Medium
Advisory: CVE-2021-33444
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-07-26
Source: https://osv.dev/vulnerability/CVE-2021-33444
Type: osv

## Details
An issue was discovered in mjs (mJS: Restricted JavaScript engine), ES6 (JavaScript version 6). There is NULL pointer dereference in getprop_builtin_foreign() in mjs.c.

## References
- https://gist.github.com/Clingto/bb632c0c463f4b2c97e4f65f751c5e6d
- https://github.com/cesanta/mjs/issues/166
