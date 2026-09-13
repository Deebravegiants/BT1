# [H] CVE-2018-14337

## Summary
Severity: High
Advisory: CVE-2018-14337
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14337
Type: osv

## Details
The CHECK macro in mrbgems/mruby-sprintf/src/sprintf.c in mruby 1.4.1 contains a signed integer overflow, possibly leading to out-of-bounds memory access because the mrb_str_resize function in string.c does not check for a negative length.

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00006.html
- https://github.com/mruby/mruby/issues/4062
