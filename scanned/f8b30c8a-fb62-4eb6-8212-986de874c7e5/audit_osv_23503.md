# [H] riscv: fix race when vmap stack overflow

## Summary
Severity: High
Advisory: CVE-2022-49001
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-49001
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: fix race when vmap stack overflow

Currently, when detecting vmap stack overflow, riscv firstly switches
to the so called shadow stack, then use this shadow stack to call the
get_overflow_stack() to get the overflow stack. However, there's
a race here if two or more harts use the same shadow stack at the same
time.

To solve this race, we introduce spin_shadow_stack atomic var, which
will be swap between its own address and 0 in atomic way, when the
var is set, it means the shadow_stack is being used; when the var
is cleared, it means the shadow_stack isn't being used.

[Palmer: Add AQ to the swap, and also some comments.]

## References
- https://git.kernel.org/stable/c/7e1864332fbc1b993659eab7974da9fe8bf8c128
- https://git.kernel.org/stable/c/879fabc5a95401d9bce357e4b1d24ae4a360a81f
- https://git.kernel.org/stable/c/ac00301adb19df54f2eae1efc4bad7447c0156ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49001.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49001
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
