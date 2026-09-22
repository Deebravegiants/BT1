# [C] CVE-2020-15866

## Summary
Severity: Critical
Advisory: CVE-2020-15866
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-21
Source: https://osv.dev/vulnerability/CVE-2020-15866
Type: osv

## Details
mruby through 2.1.2-rc has a heap-based buffer overflow in the mrb_yield_with_class function in vm.c because of incorrect VM stack handling. It can be triggered via the stack_copy function.

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00006.html
- https://github.com/mruby/mruby/issues/5042
