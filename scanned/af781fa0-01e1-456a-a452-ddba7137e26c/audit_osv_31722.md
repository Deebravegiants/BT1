# [H] pktgen: Avoid out-of-bounds access in get_imix_entries

## Summary
Severity: High
Advisory: CVE-2025-21680
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21680
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

pktgen: Avoid out-of-bounds access in get_imix_entries

Passing a sufficient amount of imix entries leads to invalid access to the
pkt_dev->imix_entries array because of the incorrect boundary check.

UBSAN: array-index-out-of-bounds in net/core/pktgen.c:874:24
index 20 is out of range for type 'imix_pkt [20]'
CPU: 2 PID: 1210 Comm: bash Not tainted 6.10.0-rc1 #121
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
Call Trace:
<TASK>
dump_stack_lvl lib/dump_stack.c:117
__ubsan_handle_out_of_bounds lib/ubsan.c:429
get_imix_entries net/core/pktgen.c:874
pktgen_if_write net/core/pktgen.c:1063
pde_write fs/proc/inode.c:334
proc_reg_write fs/proc/inode.c:346
vfs_write fs/read_write.c:593
ksys_write fs/read_write.c:644
do_syscall_64 arch/x86/entry/common.c:83
entry_SYSCALL_64_after_hwframe arch/x86/entry/entry_64.S:130

Found by Linux Verification Center (linuxtesting.org) with SVACE.

[ fp: allow to fill the array completely; minor changelog cleanup ]

## References
- https://git.kernel.org/stable/c/1a9b65c672ca9dc4ba52ca2fd54329db9580ce29
- https://git.kernel.org/stable/c/3450092cc2d1c311c5ea92a2486daa2a33520ea5
- https://git.kernel.org/stable/c/76201b5979768500bca362871db66d77cb4c225e
- https://git.kernel.org/stable/c/7cde21f52042aa2e29a654458166b873d2ae66b3
- https://git.kernel.org/stable/c/e5d24a7074dcd0c7e76b7e7e4efbbe7418d62486
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21680.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21680
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
