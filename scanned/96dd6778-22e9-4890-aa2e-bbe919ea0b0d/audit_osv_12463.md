# [H] CVE-2018-12249

## Summary
Severity: High
Advisory: CVE-2018-12249
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-12249
Type: osv

## Details
An issue was discovered in mruby 1.4.1. There is a NULL pointer dereference in mrb_class_real because "class BasicObject" is not properly supported in class.c.

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00006.html
- https://github.com/mruby/mruby/issues/4037
- https://github.com/mruby/mruby/commit/faa4eaf6803bd11669bc324b4c34e7162286bfa3
