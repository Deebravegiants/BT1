# [H] net/mlx5: Discard command completions in internal error

## Summary
Severity: High
Advisory: CVE-2024-38555
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38555
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.219, >=5.11.0 <5.15.161, >=5.12.0 <6.1.93, >=5.16.0 <6.6.33, >=6.2.0 <6.8.12, >=6.7.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Discard command completions in internal error

Fix use after free when FW completion arrives while device is in
internal error state. Avoid calling completion handler in this case,
since the device will flush the command interface and trigger all
completions manually.

Kernel log:
------------[ cut here ]------------
refcount_t: underflow; use-after-free.
...
RIP: 0010:refcount_warn_saturate+0xd8/0xe0
...
Call Trace:
<IRQ>
? __warn+0x79/0x120
? refcount_warn_saturate+0xd8/0xe0
? report_bug+0x17c/0x190
? handle_bug+0x3c/0x60
? exc_invalid_op+0x14/0x70
? asm_exc_invalid_op+0x16/0x20
? refcount_warn_saturate+0xd8/0xe0
cmd_ent_put+0x13b/0x160 [mlx5_core]
mlx5_cmd_comp_handler+0x5f9/0x670 [mlx5_core]
cmd_comp_notifier+0x1f/0x30 [mlx5_core]
notifier_call_chain+0x35/0xb0
atomic_notifier_call_chain+0x16/0x20
mlx5_eq_async_int+0xf6/0x290 [mlx5_core]
notifier_call_chain+0x35/0xb0
atomic_notifier_call_chain+0x16/0x20
irq_int_handler+0x19/0x30 [mlx5_core]
__handle_irq_event_percpu+0x4b/0x160
handle_irq_event+0x2e/0x80
handle_edge_irq+0x98/0x230
__common_interrupt+0x3b/0xa0
common_interrupt+0x7b/0xa0
</IRQ>
<TASK>
asm_common_interrupt+0x22/0x40

## References
- https://git.kernel.org/stable/c/1337ec94bc5a9eed250e33f5f5c89a28a6bfabdb
- https://git.kernel.org/stable/c/1d5dce5e92a70274de67a59e1e674c3267f94cd7
- https://git.kernel.org/stable/c/3cb92b0ad73d3f1734e812054e698d655e9581b0
- https://git.kernel.org/stable/c/7ac4c69c34240c6de820492c0a28a0bd1494265a
- https://git.kernel.org/stable/c/bf8aaf0ae01c27ae3c06aa8610caf91e50393396
- https://git.kernel.org/stable/c/db9b31aa9bc56ff0d15b78f7e827d61c4a096e40
- https://git.kernel.org/stable/c/f6fbb8535e990f844371086ab2c1221f71f993d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38555.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38555
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
