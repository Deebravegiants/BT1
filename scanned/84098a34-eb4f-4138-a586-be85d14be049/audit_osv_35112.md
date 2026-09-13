# [H] jbd2: avoid bug_on in jbd2_journal_get_create_access() when file system corrupted

## Summary
Severity: High
Advisory: CVE-2025-68337
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2025-68337
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.62, >=6.13.0 <6.17.12, >=6.18.0 <6.18.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

jbd2: avoid bug_on in jbd2_journal_get_create_access() when file system corrupted

There's issue when file system corrupted:
------------[ cut here ]------------
kernel BUG at fs/jbd2/transaction.c:1289!
Oops: invalid opcode: 0000 [#1] SMP KASAN PTI
CPU: 5 UID: 0 PID: 2031 Comm: mkdir Not tainted 6.18.0-rc1-next
RIP: 0010:jbd2_journal_get_create_access+0x3b6/0x4d0
RSP: 0018:ffff888117aafa30 EFLAGS: 00010202
RAX: 0000000000000000 RBX: ffff88811a86b000 RCX: ffffffff89a63534
RDX: 1ffff110200ec602 RSI: 0000000000000004 RDI: ffff888100763010
RBP: ffff888100763000 R08: 0000000000000001 R09: ffff888100763028
R10: 0000000000000003 R11: 0000000000000000 R12: 0000000000000000
R13: ffff88812c432000 R14: ffff88812c608000 R15: ffff888120bfc000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 00007f91d6970c99 CR3: 00000001159c4000 CR4: 00000000000006f0
Call Trace:
 <TASK>
 __ext4_journal_get_create_access+0x42/0x170
 ext4_getblk+0x319/0x6f0
 ext4_bread+0x11/0x100
 ext4_append+0x1e6/0x4a0
 ext4_init_new_dir+0x145/0x1d0
 ext4_mkdir+0x326/0x920
 vfs_mkdir+0x45c/0x740
 do_mkdirat+0x234/0x2f0
 __x64_sys_mkdir+0xd6/0x120
 do_syscall_64+0x5f/0xfa0
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

The above issue occurs with us in errors=continue mode when accompanied by
storage failures. There have been many inconsistencies in the file system
data.
In the case of file system data inconsistency, for example, if the block
bitmap of a referenced block is not set, it can lead to the situation where
a block being committed is allocated and used again. As a result, the
following condition will not be satisfied then trigger BUG_ON. Of course,
it is entirely possible to construct a problematic image that can trigger
this BUG_ON through specific operations. In fact, I have constructed such
an image and easily reproduced this issue.
Therefore, J_ASSERT() holds true only under ideal conditions, but it may
not necessarily be satisfied in exceptional scenarios. Using J_ASSERT()
directly in abnormal situations would cause the system to crash, which is
clearly not what we want. So here we directly trigger a JBD abort instead
of immediately invoking BUG_ON.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/3faac6531d4818cd6be45e5bbf32937bbbc795c0
- https://git.kernel.org/stable/c/71bbe06c40fc59b5b15661eca8ff307f4176d7f9
- https://git.kernel.org/stable/c/986835bf4d11032bba4ab8414d18fce038c61bb4
- https://git.kernel.org/stable/c/a2a7f854d154a3e9232fec80782dad951655f52f
- https://git.kernel.org/stable/c/aa1703f3f706ea0867fb1991dcac709c9ec94cfb
- https://git.kernel.org/stable/c/b4f8eabf6d991bd41fabcdf9302c4b3eab590cf4
- https://git.kernel.org/stable/c/bf34c72337e40c4670cceeb79b353356933a254b
- https://git.kernel.org/stable/c/ed62fd8c15d41c4127ad16b8219b63124f5962bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68337.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68337
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
