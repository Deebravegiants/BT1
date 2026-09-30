# [H] f2fs: validate ACL entry sizes in f2fs_acl_from_disk()

## Summary
Severity: High
Advisory: CVE-2026-63814
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63814
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: validate ACL entry sizes in f2fs_acl_from_disk()

f2fs_acl_count() only validates the aggregate ACL xattr length. A
malformed ACL can still place ACL_USER or ACL_GROUP in a slot that only
contains struct f2fs_acl_entry_short bytes, and f2fs_acl_from_disk()
then reads entry->e_id before verifying that a full entry fits.

Require a short entry before reading e_tag and e_perm, and require a
full entry before reading e_id for ACL_USER and ACL_GROUP. Return
-EFSCORRUPTED from these new truncated-entry checks, while keeping the
pre-existing -EINVAL paths unchanged.

Validation reproduced this kernel report:
KASAN slab-out-of-bounds in __f2fs_get_acl+0x6fb/0x7e0
RIP: 0033:0x7f4b835ea7aa
The buggy address belongs to the object at ffff888114589960 which belongs
to the cache kmalloc-8 of size 8
The buggy address is located 0 bytes to the right of allocated 8-byte
region [ffff888114589960, ffff888114589968)
Read of size 4
Call trace:
  dump_stack_lvl+0x66/0xa0 (?:?)
  print_report+0xce/0x630 (?:?)
  __f2fs_get_acl+0x6fb/0x7e0 (fs/f2fs/acl.c:169)
  srso_alias_return_thunk+0x5/0xfbef5 (?:?)
  __virt_addr_valid+0x224/0x430 (?:?)
  kasan_report+0xe0/0x110 (?:?)
  __f2fs_get_acl+0x5/0x7e0 (fs/f2fs/acl.c:169)
  __get_acl+0x281/0x380 (?:?)
  vfs_get_acl+0x10b/0x190 (?:?)
  do_get_acl+0x2a/0x410 (?:?)
  do_get_acl+0x9/0x410 (?:?)
  do_getxattr+0xe8/0x260 (?:?)
  filename_getxattr+0xd1/0x140 (?:?)
  do_getname+0x2d/0x2d0 (?:?)
  path_getxattrat+0x16c/0x200 (?:?)
  lock_release+0xc8/0x290 (?:?)
  cgroup_update_frozen+0x9d/0x320 (?:?)
  lockdep_hardirqs_on_prepare+0xea/0x1a0 (?:?)
  trace_hardirqs_on+0x1a/0x170 (?:?)
  _raw_spin_unlock_irq+0x28/0x50 (?:?)
  do_syscall_64+0x115/0x6a0 (arch/x86/entry/syscall_64.c:87)
  entry_SYSCALL_64_after_hwframe+0x77/0x7f (?:?)

## References
- https://git.kernel.org/stable/c/1ddf3fd21c4c652f9cab5552515c04a166662306
- https://git.kernel.org/stable/c/442ca20c54038e2400cf28aaa944cf1de2c8e65d
- https://git.kernel.org/stable/c/4e2a96ec7236e248e706850568e0a925fd21b588
- https://git.kernel.org/stable/c/5d8a39649947a4e86c8fbc682d7fc0041b8d109a
- https://git.kernel.org/stable/c/733cd8474e6d763d75ed96f3f2b98a25480cf2b9
- https://git.kernel.org/stable/c/aba4f94ac1832c7299c33e1b4fe5f87eef6dc8f1
- https://git.kernel.org/stable/c/c4810ada31e80cbe4011467c4f3b1e93f94134f3
- https://git.kernel.org/stable/c/ff83de56882cb8466184d322abece2589258ca56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63814.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63814
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
