# [H] bnxt_en: Fix out-of-bound memcpy() during ethtool -w

## Summary
Severity: High
Advisory: CVE-2025-37911
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37911
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.15.182, >=5.16.0 <6.1.138, >=6.2.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bnxt_en: Fix out-of-bound memcpy() during ethtool -w

When retrieving the FW coredump using ethtool, it can sometimes cause
memory corruption:

BUG: KFENCE: memory corruption in __bnxt_get_coredump+0x3ef/0x670 [bnxt_en]
Corrupted memory at 0x000000008f0f30e8 [ ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ] (in kfence-#45):
__bnxt_get_coredump+0x3ef/0x670 [bnxt_en]
ethtool_get_dump_data+0xdc/0x1a0
__dev_ethtool+0xa1e/0x1af0
dev_ethtool+0xa8/0x170
dev_ioctl+0x1b5/0x580
sock_do_ioctl+0xab/0xf0
sock_ioctl+0x1ce/0x2e0
__x64_sys_ioctl+0x87/0xc0
do_syscall_64+0x5c/0xf0
entry_SYSCALL_64_after_hwframe+0x78/0x80

...

This happens when copying the coredump segment list in
bnxt_hwrm_dbg_dma_data() with the HWRM_DBG_COREDUMP_LIST FW command.
The info->dest_buf buffer is allocated based on the number of coredump
segments returned by the FW.  The segment list is then DMA'ed by
the FW and the length of the DMA is returned by FW.  The driver then
copies this DMA'ed segment list to info->dest_buf.

In some cases, this DMA length may exceed the info->dest_buf length
and cause the above BUG condition.  Fix it by capping the copy
length to not exceed the length of info->dest_buf.  The extra
DMA data contains no useful information.

This code path is shared for the HWRM_DBG_COREDUMP_LIST and the
HWRM_DBG_COREDUMP_RETRIEVE FW commands.  The buffering is different
for these 2 FW commands.  To simplify the logic, we need to move
the line to adjust the buffer length for HWRM_DBG_COREDUMP_RETRIEVE
up, so that the new check to cap the copy length will work for both
commands.

## References
- https://git.kernel.org/stable/c/43292b83424158fa6ec458799f3cb9c54d18c484
- https://git.kernel.org/stable/c/44807af79efd0d78fa36383dd865ddfe7992c0a6
- https://git.kernel.org/stable/c/44d81a9ebf0cad92512e0ffdf7412bfe20db66ec
- https://git.kernel.org/stable/c/4d69864915a3a052538e4ba76cd6fd77cfc64ebe
- https://git.kernel.org/stable/c/69b10dd23ab826d0c7f2d9ab311842251978d0c1
- https://git.kernel.org/stable/c/6b87bd94f34370bbf1dfa59352bed8efab5bf419
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37911.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37911
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
