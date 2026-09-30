# [C] crypto: xilinx - call finalize with bh disabled

## Summary
Severity: Critical
Advisory: CVE-2024-26877
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26877
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: xilinx - call finalize with bh disabled

When calling crypto_finalize_request, BH should be disabled to avoid
triggering the following calltrace:

    ------------[ cut here ]------------
    WARNING: CPU: 2 PID: 74 at crypto/crypto_engine.c:58 crypto_finalize_request+0xa0/0x118
    Modules linked in: cryptodev(O)
    CPU: 2 PID: 74 Comm: firmware:zynqmp Tainted: G           O       6.8.0-rc1-yocto-standard #323
    Hardware name: ZynqMP ZCU102 Rev1.0 (DT)
    pstate: 40000005 (nZcv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
    pc : crypto_finalize_request+0xa0/0x118
    lr : crypto_finalize_request+0x104/0x118
    sp : ffffffc085353ce0
    x29: ffffffc085353ce0 x28: 0000000000000000 x27: ffffff8808ea8688
    x26: ffffffc081715038 x25: 0000000000000000 x24: ffffff880100db00
    x23: ffffff880100da80 x22: 0000000000000000 x21: 0000000000000000
    x20: ffffff8805b14000 x19: ffffff880100da80 x18: 0000000000010450
    x17: 0000000000000000 x16: 0000000000000000 x15: 0000000000000000
    x14: 0000000000000003 x13: 0000000000000000 x12: ffffff880100dad0
    x11: 0000000000000000 x10: ffffffc0832dcd08 x9 : ffffffc0812416d8
    x8 : 00000000000001f4 x7 : ffffffc0830d2830 x6 : 0000000000000001
    x5 : ffffffc082091000 x4 : ffffffc082091658 x3 : 0000000000000000
    x2 : ffffffc7f9653000 x1 : 0000000000000000 x0 : ffffff8802d20000
    Call trace:
     crypto_finalize_request+0xa0/0x118
     crypto_finalize_aead_request+0x18/0x30
     zynqmp_handle_aes_req+0xcc/0x388
     crypto_pump_work+0x168/0x2d8
     kthread_worker_fn+0xfc/0x3a0
     kthread+0x118/0x138
     ret_from_fork+0x10/0x20
    irq event stamp: 40
    hardirqs last  enabled at (39): [<ffffffc0812416f8>] _raw_spin_unlock_irqrestore+0x70/0xb0
    hardirqs last disabled at (40): [<ffffffc08122d208>] el1_dbg+0x28/0x90
    softirqs last  enabled at (36): [<ffffffc080017dec>] kernel_neon_begin+0x8c/0xf0
    softirqs last disabled at (34): [<ffffffc080017dc0>] kernel_neon_begin+0x60/0xf0
    ---[ end trace 0000000000000000 ]---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/03e6d4e948432a61b35783323b6ab2be071d2619
- https://git.kernel.org/stable/c/23bc89fdce71124cd2126fc919c7076e7cb489cf
- https://git.kernel.org/stable/c/8a01335aedc50a66d04dd39203c89f4bc8042596
- https://git.kernel.org/stable/c/9db89b1fb85557892e6681724b367287de5f9f20
- https://git.kernel.org/stable/c/a71f66bd5f7b9b35a8aaa49e29565eca66299399
- https://git.kernel.org/stable/c/a853450bf4c752e664abab0b2fad395b7ad7701c
- https://git.kernel.org/stable/c/dbf291d8ffffb70f48286176a15c6c54f0bb0743
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26877.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26877
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
