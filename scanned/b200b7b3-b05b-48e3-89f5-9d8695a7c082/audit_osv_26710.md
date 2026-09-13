# [H] ASoC: lpass: Fix for KASAN use_after_free out of bounds

## Summary
Severity: High
Advisory: CVE-2023-53640
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53640
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.114, >=5.16.0 <6.1.31, >=6.2.0 <6.3.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: lpass: Fix for KASAN use_after_free out of bounds

When we run syzkaller we get below Out of Bounds error.

"KASAN: slab-out-of-bounds Read in regcache_flat_read"

Below is the backtrace of the issue:

BUG: KASAN: slab-out-of-bounds in regcache_flat_read+0x10c/0x110
Read of size 4 at addr ffffff8088fbf714 by task syz-executor.4/14144
CPU: 6 PID: 14144 Comm: syz-executor.4 Tainted: G        W
Hardware name: Qualcomm Technologies, Inc. sc7280 CRD platform (rev5+) (DT)
Call trace:
dump_backtrace+0x0/0x4ec
show_stack+0x34/0x50
dump_stack_lvl+0xdc/0x11c
print_address_description+0x30/0x2d8
kasan_report+0x178/0x1e4
__asan_report_load4_noabort+0x44/0x50
regcache_flat_read+0x10c/0x110
regcache_read+0xf8/0x5a0
_regmap_read+0x45c/0x86c
_regmap_update_bits+0x128/0x290
regmap_update_bits_base+0xc0/0x15c
snd_soc_component_update_bits+0xa8/0x22c
snd_soc_component_write_field+0x68/0xd4
tx_macro_put_dec_enum+0x1d0/0x268
snd_ctl_elem_write+0x288/0x474

By Error checking and checking valid values issue gets rectifies.

## References
- https://git.kernel.org/stable/c/75e5fab7db0cecb6e16b22c34608f0b40a4c7cd1
- https://git.kernel.org/stable/c/8d81d3b0ed3610d24191d24f8e9e20f6775f0cc5
- https://git.kernel.org/stable/c/8f1512d78b5de928f4616a871e77b58fd546e651
- https://git.kernel.org/stable/c/f5e61e3fe799ba2fda4320af23d26d28c3302045
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53640.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53640
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
