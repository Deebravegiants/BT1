# [H] CVE-2021-46020

## Summary
Severity: High
Advisory: CVE-2021-46020
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2021-46020
Type: osv

## Details
An untrusted pointer dereference in mrb_vm_exec() of mruby v3.0.0 can lead to a segmentation fault or application crash.

## References
- https://github.com/mruby/mruby/issues/5613
