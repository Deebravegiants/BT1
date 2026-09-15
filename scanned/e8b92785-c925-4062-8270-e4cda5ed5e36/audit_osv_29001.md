# [H] jffs2: prevent xattr node from overflowing the eraseblock

## Summary
Severity: High
Advisory: CVE-2024-38599
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38599
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.18 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

jffs2: prevent xattr node from overflowing the eraseblock

Add a check to make sure that the requested xattr node size is no larger
than the eraseblock minus the cleanmarker.

Unlike the usual inode nodes, the xattr nodes aren't split into parts
and spread across multiple eraseblocks, which means that a xattr node
must not occupy more than one eraseblock. If the requested xattr value is
too large, the xattr node can spill onto the next eraseblock, overwriting
the nodes and causing errors such as:

jffs2: argh. node added in wrong place at 0x0000b050(2)
jffs2: nextblock 0x0000a000, expected at 0000b00c
jffs2: error: (823) do_verify_xattr_datum: node CRC failed at 0x01e050,
read=0xfc892c93, calc=0x000000
jffs2: notice: (823) jffs2_get_inode_nodes: Node header CRC failed
at 0x01e00c. {848f,2fc4,0fef511f,59a3d171}
jffs2: Node at 0x0000000c with length 0x00001044 would run over the
end of the erase block
jffs2: Perhaps the file system was created with the wrong erase size?
jffs2: jffs2_scan_eraseblock(): Magic bitmask 0x1985 not found
at 0x00000010: 0x1044 instead

This breaks the filesystem and can lead to KASAN crashes such as:

BUG: KASAN: slab-out-of-bounds in jffs2_sum_add_kvec+0x125e/0x15d0
Read of size 4 at addr ffff88802c31e914 by task repro/830
CPU: 0 PID: 830 Comm: repro Not tainted 6.9.0-rc3+ #1
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996),
BIOS Arch Linux 1.16.3-1-1 04/01/2014
Call Trace:
 <TASK>
 dump_stack_lvl+0xc6/0x120
 print_report+0xc4/0x620
 ? __virt_addr_valid+0x308/0x5b0
 kasan_report+0xc1/0xf0
 ? jffs2_sum_add_kvec+0x125e/0x15d0
 ? jffs2_sum_add_kvec+0x125e/0x15d0
 jffs2_sum_add_kvec+0x125e/0x15d0
 jffs2_flash_direct_writev+0xa8/0xd0
 jffs2_flash_writev+0x9c9/0xef0
 ? __x64_sys_setxattr+0xc4/0x160
 ? do_syscall_64+0x69/0x140
 ? entry_SYSCALL_64_after_hwframe+0x76/0x7e
 [...]

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/2904e1d9b64f72d291095e3cbb31634f08788b11
- https://git.kernel.org/stable/c/526235dffcac74c7823ed504dfac4f88d84ba5df
- https://git.kernel.org/stable/c/8d431391320c5c5398ff966fb3a95e68a7def275
- https://git.kernel.org/stable/c/978a12c91b38bf1a213e567f3c20e2beef215f07
- https://git.kernel.org/stable/c/a1d21bcd78cf4a4353e1e835789429c6b76aca8b
- https://git.kernel.org/stable/c/af82d8d2179b7277ad627c39e7e0778f1c86ccdb
- https://git.kernel.org/stable/c/c6854e5a267c28300ff045480b5a7ee7f6f1d913
- https://git.kernel.org/stable/c/f06969df2e40ab1dc8f4364a5de967830c74a098
- https://git.kernel.org/stable/c/f0eea095ce8c959b86e1e57fe36ca4fea5ae54f8
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38599.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38599
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
