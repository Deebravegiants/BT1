# [H] jffs2: Fix potential illegal address access in jffs2_free_inode

## Summary
Severity: High
Advisory: CVE-2024-42115
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42115
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.318, >=4.20.0 <5.4.280, >=5.1.0 <5.10.222, >=5.5.0 <5.15.163, >=5.11.0 <6.1.98, >=5.16.0 <6.6.39, >=6.2.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

jffs2: Fix potential illegal address access in jffs2_free_inode

During the stress testing of the jffs2 file system,the following
abnormal printouts were found:
[ 2430.649000] Unable to handle kernel paging request at virtual address 0069696969696948
[ 2430.649622] Mem abort info:
[ 2430.649829]   ESR = 0x96000004
[ 2430.650115]   EC = 0x25: DABT (current EL), IL = 32 bits
[ 2430.650564]   SET = 0, FnV = 0
[ 2430.650795]   EA = 0, S1PTW = 0
[ 2430.651032]   FSC = 0x04: level 0 translation fault
[ 2430.651446] Data abort info:
[ 2430.651683]   ISV = 0, ISS = 0x00000004
[ 2430.652001]   CM = 0, WnR = 0
[ 2430.652558] [0069696969696948] address between user and kernel address ranges
[ 2430.653265] Internal error: Oops: 96000004 [#1] PREEMPT SMP
[ 2430.654512] CPU: 2 PID: 20919 Comm: cat Not tainted 5.15.25-g512f31242bf6 #33
[ 2430.655008] Hardware name: linux,dummy-virt (DT)
[ 2430.655517] pstate: 20000005 (nzCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
[ 2430.656142] pc : kfree+0x78/0x348
[ 2430.656630] lr : jffs2_free_inode+0x24/0x48
[ 2430.657051] sp : ffff800009eebd10
[ 2430.657355] x29: ffff800009eebd10 x28: 0000000000000001 x27: 0000000000000000
[ 2430.658327] x26: ffff000038f09d80 x25: 0080000000000000 x24: ffff800009d38000
[ 2430.658919] x23: 5a5a5a5a5a5a5a5a x22: ffff000038f09d80 x21: ffff8000084f0d14
[ 2430.659434] x20: ffff0000bf9a6ac0 x19: 0169696969696940 x18: 0000000000000000
[ 2430.659969] x17: ffff8000b6506000 x16: ffff800009eec000 x15: 0000000000004000
[ 2430.660637] x14: 0000000000000000 x13: 00000001000820a1 x12: 00000000000d1b19
[ 2430.661345] x11: 0004000800000000 x10: 0000000000000001 x9 : ffff8000084f0d14
[ 2430.662025] x8 : ffff0000bf9a6b40 x7 : ffff0000bf9a6b48 x6 : 0000000003470302
[ 2430.662695] x5 : ffff00002e41dcc0 x4 : ffff0000bf9aa3b0 x3 : 0000000003470342
[ 2430.663486] x2 : 0000000000000000 x1 : ffff8000084f0d14 x0 : fffffc0000000000
[ 2430.664217] Call trace:
[ 2430.664528]  kfree+0x78/0x348
[ 2430.664855]  jffs2_free_inode+0x24/0x48
[ 2430.665233]  i_callback+0x24/0x50
[ 2430.665528]  rcu_do_batch+0x1ac/0x448
[ 2430.665892]  rcu_core+0x28c/0x3c8
[ 2430.666151]  rcu_core_si+0x18/0x28
[ 2430.666473]  __do_softirq+0x138/0x3cc
[ 2430.666781]  irq_exit+0xf0/0x110
[ 2430.667065]  handle_domain_irq+0x6c/0x98
[ 2430.667447]  gic_handle_irq+0xac/0xe8
[ 2430.667739]  call_on_irq_stack+0x28/0x54
The parameter passed to kfree was 5a5a5a5a, which corresponds to the target field of
the jffs_inode_info structure. It was found that all variables in the jffs_inode_info
structure were 5a5a5a5a, except for the first member sem. It is suspected that these
variables are not initialized because they were set to 5a5a5a5a during memory testing,
which is meant to detect uninitialized memory.The sem variable is initialized in the
function jffs2_i_init_once, while other members are initialized in
the function jffs2_init_inode_info.

The function jffs2_init_inode_info is called after iget_locked,
but in the iget_locked function, the destroy_inode process is triggered,
which releases the inode and consequently, the target member of the inode
is not initialized.In concurrent high pressure scenarios, iget_locked
may enter the destroy_inode branch as described in the code.

Since the destroy_inode functionality of jffs2 only releases the target,
the fix method is to set target to NULL in jffs2_i_init_once.

## References
- https://git.kernel.org/stable/c/05fc1ef892f862c1197b11b288bc00f602d2df0c
- https://git.kernel.org/stable/c/0b3246052e01e61a55bb3a15b76acb006759fe67
- https://git.kernel.org/stable/c/5ca26334fc8a3711fed14db7f9eb1c621be4df65
- https://git.kernel.org/stable/c/6d6d94287f6365282bbf41e9a5b5281985970789
- https://git.kernel.org/stable/c/751987a5d8ead0cc405fad96e83ebbaa51c82dbc
- https://git.kernel.org/stable/c/af9a8730ddb6a4b2edd779ccc0aceb994d616830
- https://git.kernel.org/stable/c/b6c8b3e31eb88c85094d848a0bd8b4bafe67e4d8
- https://git.kernel.org/stable/c/d0bbbf31462a400bef4df33e22de91864f475455
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42115.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42115
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
