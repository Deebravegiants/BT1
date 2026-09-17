# [M] mtd: spi-nor: sst: Fix SST write failure

## Summary
Severity: Medium
Advisory: CVE-2025-21845
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21845
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: spi-nor: sst: Fix SST write failure

'commit 18bcb4aa54ea ("mtd: spi-nor: sst: Factor out common write operation
to `sst_nor_write_data()`")' introduced a bug where only one byte of data
is written, regardless of the number of bytes passed to
sst_nor_write_data(), causing a kernel crash during the write operation.
Ensure the correct number of bytes are written as passed to
sst_nor_write_data().

Call trace:
[   57.400180] ------------[ cut here ]------------
[   57.404842] While writing 2 byte written 1 bytes
[   57.409493] WARNING: CPU: 0 PID: 737 at drivers/mtd/spi-nor/sst.c:187 sst_nor_write_data+0x6c/0x74
[   57.418464] Modules linked in:
[   57.421517] CPU: 0 UID: 0 PID: 737 Comm: mtd_debug Not tainted 6.12.0-g5ad04afd91f9 #30
[   57.429517] Hardware name: Xilinx Versal A2197 Processor board revA - x-prc-02 revA (DT)
[   57.437600] pstate: 60000005 (nZCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
[   57.444557] pc : sst_nor_write_data+0x6c/0x74
[   57.448911] lr : sst_nor_write_data+0x6c/0x74
[   57.453264] sp : ffff80008232bb40
[   57.456570] x29: ffff80008232bb40 x28: 0000000000010000 x27: 0000000000000001
[   57.463708] x26: 000000000000ffff x25: 0000000000000000 x24: 0000000000000000
[   57.470843] x23: 0000000000010000 x22: ffff80008232bbf0 x21: ffff000816230000
[   57.477978] x20: ffff0008056c0080 x19: 0000000000000002 x18: 0000000000000006
[   57.485112] x17: 0000000000000000 x16: 0000000000000000 x15: ffff80008232b580
[   57.492246] x14: 0000000000000000 x13: ffff8000816d1530 x12: 00000000000004a4
[   57.499380] x11: 000000000000018c x10: ffff8000816fd530 x9 : ffff8000816d1530
[   57.506515] x8 : 00000000fffff7ff x7 : ffff8000816fd530 x6 : 0000000000000001
[   57.513649] x5 : 0000000000000000 x4 : 0000000000000000 x3 : 0000000000000000
[   57.520782] x2 : 0000000000000000 x1 : 0000000000000000 x0 : ffff0008049b0000
[   57.527916] Call trace:
[   57.530354]  sst_nor_write_data+0x6c/0x74
[   57.534361]  sst_nor_write+0xb4/0x18c
[   57.538019]  mtd_write_oob_std+0x7c/0x88
[   57.541941]  mtd_write_oob+0x70/0xbc
[   57.545511]  mtd_write+0x68/0xa8
[   57.548733]  mtdchar_write+0x10c/0x290
[   57.552477]  vfs_write+0xb4/0x3a8
[   57.555791]  ksys_write+0x74/0x10c
[   57.559189]  __arm64_sys_write+0x1c/0x28
[   57.563109]  invoke_syscall+0x54/0x11c
[   57.566856]  el0_svc_common.constprop.0+0xc0/0xe0
[   57.571557]  do_el0_svc+0x1c/0x28
[   57.574868]  el0_svc+0x30/0xcc
[   57.577921]  el0t_64_sync_handler+0x120/0x12c
[   57.582276]  el0t_64_sync+0x190/0x194
[   57.585933] ---[ end trace 0000000000000000 ]---

[pratyush@kernel.org: add Cc stable tag]

## References
- https://git.kernel.org/stable/c/539bd20352832b9244238a055eb169ccf1c41ff6
- https://git.kernel.org/stable/c/9553391f32f8c43e12fc7c04e1035160b5ea20bf
- https://git.kernel.org/stable/c/bb1accc7e0f688886f0c634f2e878b8ac4ee6a58
- https://git.kernel.org/stable/c/f791837015a0d20f584d0ed368393f119a00018f
- https://git.kernel.org/stable/c/f7c14993dc2f1eca661975c0ff90a6e2098ecd41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21845.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21845
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
