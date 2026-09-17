# [C] CVE-2018-10191

## Summary
Severity: Critical
Advisory: CVE-2018-10191
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-17
Source: https://osv.dev/vulnerability/CVE-2018-10191
Type: osv

## Details
In versions of mruby up to and including 1.4.0, an integer overflow exists in src/vm.c::mrb_vm_exec() when handling OP_GETUPVAR in the presence of deep scope nesting, resulting in a use-after-free. An attacker that can cause Ruby code to be run can use this to possibly execute arbitrary code.

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00006.html
- https://github.com/mruby/mruby/issues/3995
- https://github.com/mruby/mruby/commit/1905091634a6a2925c911484434448e568330626
