# [M] CVE-2021-47264

## Summary
Severity: Medium
Advisory: CVE-2021-47264
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47264
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: core: Fix Null-point-dereference in fmt_single_name()

Check the return value of devm_kstrdup() in case of
Null-point-dereference.

## References
- https://git.kernel.org/stable/c/047fd16015a79180771650aa6ce71f68b2c23368
- https://git.kernel.org/stable/c/0e2c9aeb00289f279b8181fbd4c20765127d8943
- https://git.kernel.org/stable/c/41daf6ba594d55f201c50280ebcd430590441da1
