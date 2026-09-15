# [H] kprobes: Fix possible use-after-free issue on kprobe registration

## Summary
Severity: High
Advisory: CVE-2024-35955
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35955
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.157, >=5.16.0 <6.1.87, >=6.0.0 <6.6.28, >=6.2.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

kprobes: Fix possible use-after-free issue on kprobe registration

When unloading a module, its state is changing MODULE_STATE_LIVE ->
 MODULE_STATE_GOING -> MODULE_STATE_UNFORMED. Each change will take
a time. `is_module_text_address()` and `__module_text_address()`
works with MODULE_STATE_LIVE and MODULE_STATE_GOING.
If we use `is_module_text_address()` and `__module_text_address()`
separately, there is a chance that the first one is succeeded but the
next one is failed because module->state becomes MODULE_STATE_UNFORMED
between those operations.

In `check_kprobe_address_safe()`, if the second `__module_text_address()`
is failed, that is ignored because it expected a kernel_text address.
But it may have failed simply because module->state has been changed
to MODULE_STATE_UNFORMED. In this case, arm_kprobe() will try to modify
non-exist module text address (use-after-free).

To fix this problem, we should not use separated `is_module_text_address()`
and `__module_text_address()`, but use only `__module_text_address()`
once and do `try_module_get(module)` which is only available with
MODULE_STATE_LIVE.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/2df2dd27066cdba8041e46a64362325626bdfb2e
- https://git.kernel.org/stable/c/325f3fb551f8cd672dbbfc4cf58b14f9ee3fc9e8
- https://git.kernel.org/stable/c/36b57c7d2f8b7de224980f1a284432846ad71ca0
- https://git.kernel.org/stable/c/5062d1f4f07facbdade0f402d9a04a788f52e26d
- https://git.kernel.org/stable/c/62029bc9ff2c17a4e3a2478d83418ec575413808
- https://git.kernel.org/stable/c/93eb31e7c3399e326259f2caa17be1e821f5a412
- https://git.kernel.org/stable/c/b5808d40093403334d939e2c3c417144d12a6f33
- https://git.kernel.org/stable/c/d15023fb407337028a654237d8968fefdcf87c2f
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35955.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35955
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
