# [H] CVE-2018-12248

## Summary
Severity: High
Advisory: CVE-2018-12248
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-12248
Type: osv

## Details
An issue was discovered in mruby 1.4.1. There is a heap-based buffer over-read associated with OP_ENTER because mrbgems/mruby-fiber/src/fiber.c does not extend the stack in cases of many arguments to fiber.

## References
- https://github.com/mruby/mruby/issues/4038
- https://github.com/mruby/mruby/commit/778500563a9f7ceba996937dc886bd8cde29b42b
