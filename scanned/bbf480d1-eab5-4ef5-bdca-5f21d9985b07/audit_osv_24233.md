# [H] RDMA/rxe: Fix mr->map double free

## Summary
Severity: High
Advisory: CVE-2022-50543
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2022-50543
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix mr->map double free

rxe_mr_cleanup() which tries to free mr->map again will be called when
rxe_mr_init_user() fails:

   CPU: 0 PID: 4917 Comm: rdma_flush_serv Kdump: loaded Not tainted 6.1.0-rc1-roce-flush+ #25
   Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.16.0-0-gd239552ce722-prebuilt.qemu.org 04/01/2014
   Call Trace:
    <TASK>
    dump_stack_lvl+0x45/0x5d
    panic+0x19e/0x349
    end_report.part.0+0x54/0x7c
    kasan_report.cold+0xa/0xf
    rxe_mr_cleanup+0x9d/0xf0 [rdma_rxe]
    __rxe_cleanup+0x10a/0x1e0 [rdma_rxe]
    rxe_reg_user_mr+0xb7/0xd0 [rdma_rxe]
    ib_uverbs_reg_mr+0x26a/0x480 [ib_uverbs]
    ib_uverbs_handler_UVERBS_METHOD_INVOKE_WRITE+0x1a2/0x250 [ib_uverbs]
    ib_uverbs_cmd_verbs+0x1397/0x15a0 [ib_uverbs]

This issue was firstly exposed since commit b18c7da63fcb ("RDMA/rxe: Fix
memory leak in error path code") and then we fixed it in commit
8ff5f5d9d8cf ("RDMA/rxe: Prevent double freeing rxe_map_set()") but this
fix was reverted together at last by commit 1e75550648da (Revert
"RDMA/rxe: Create duplicate mapping tables for FMRs")

Simply let rxe_mr_cleanup() always handle freeing the mr->map once it is
successfully allocated.

## References
- https://git.kernel.org/stable/c/06f73568f553b5be6ba7f6fe274d333ea29fc46d
- https://git.kernel.org/stable/c/6ce577f09013206e36e674cd27da3707b2278268
- https://git.kernel.org/stable/c/7d984dac8f6bf4ebd3398af82b357e1d181ecaac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50543.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50543
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
