# [H] HID: intel-thc-hid: intel-thc: Fix incorrect pointer arithmetic in I2C regs save

## Summary
Severity: High
Advisory: CVE-2025-39818
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39818
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: intel-thc-hid: intel-thc: Fix incorrect pointer arithmetic in I2C regs save

Improper use of secondary pointer (&dev->i2c_subip_regs) caused
kernel crash and out-of-bounds error:

 BUG: KASAN: slab-out-of-bounds in _regmap_bulk_read+0x449/0x510
 Write of size 4 at addr ffff888136005dc0 by task kworker/u33:5/5107

 CPU: 3 UID: 0 PID: 5107 Comm: kworker/u33:5 Not tainted 6.16.0+ #3 PREEMPT(voluntary)
 Workqueue: async async_run_entry_fn
 Call Trace:
  <TASK>
  dump_stack_lvl+0x76/0xa0
  print_report+0xd1/0x660
  ? __pfx__raw_spin_lock_irqsave+0x10/0x10
  ? kasan_complete_mode_report_info+0x26/0x200
  kasan_report+0xe1/0x120
  ? _regmap_bulk_read+0x449/0x510
  ? _regmap_bulk_read+0x449/0x510
  __asan_report_store4_noabort+0x17/0x30
  _regmap_bulk_read+0x449/0x510
  ? __pfx__regmap_bulk_read+0x10/0x10
  regmap_bulk_read+0x270/0x3d0
  pio_complete+0x1ee/0x2c0 [intel_thc]
  ? __pfx_pio_complete+0x10/0x10 [intel_thc]
  ? __pfx_pio_wait+0x10/0x10 [intel_thc]
  ? regmap_update_bits_base+0x13b/0x1f0
  thc_i2c_subip_pio_read+0x117/0x270 [intel_thc]
  thc_i2c_subip_regs_save+0xc2/0x140 [intel_thc]
  ? __pfx_thc_i2c_subip_regs_save+0x10/0x10 [intel_thc]
[...]
 The buggy address belongs to the object at ffff888136005d00
  which belongs to the cache kmalloc-rnd-12-192 of size 192
 The buggy address is located 0 bytes to the right of
  allocated 192-byte region [ffff888136005d00, ffff888136005dc0)

Replaced with direct array indexing (&dev->i2c_subip_regs[i]) to ensure
safe memory access.

## References
- https://git.kernel.org/stable/c/78d4cf0466c79452e47aa6f720afbde63e709ccc
- https://git.kernel.org/stable/c/a7fc15ed629be89e51e09b743277c53e0a0168f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39818.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39818
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
