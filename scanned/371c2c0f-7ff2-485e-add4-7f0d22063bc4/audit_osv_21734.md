# [H] CVE-2021-46023

## Summary
Severity: High
Advisory: CVE-2021-46023
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/CVE-2021-46023
Type: osv

## Details
An Untrusted Pointer Dereference was discovered in function mrb_vm_exec in mruby before 3.1.0-rc. The vulnerability causes a segmentation fault and application crash.

## References
- https://github.com/mruby/mruby/issues/5613
