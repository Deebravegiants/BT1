# [H] ext4: fix WARNING in ext4_update_inline_data

## Summary
Severity: High
Advisory: CVE-2023-53100
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53100
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.14.310, >=4.15.0 <4.19.278, >=4.20.0 <5.4.237, >=5.5.0 <5.10.175, >=5.11.0 <5.15.103, >=5.16.0 <6.1.20, >=6.2.0 <6.2.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix WARNING in ext4_update_inline_data

Syzbot found the following issue:
EXT4-fs (loop0): mounted filesystem 00000000-0000-0000-0000-000000000000 without journal. Quota mode: none.
fscrypt: AES-256-CTS-CBC using implementation "cts-cbc-aes-aesni"
fscrypt: AES-256-XTS using implementation "xts-aes-aesni"
------------[ cut here ]------------
WARNING: CPU: 0 PID: 5071 at mm/page_alloc.c:5525 __alloc_pages+0x30a/0x560 mm/page_alloc.c:5525
Modules linked in:
CPU: 1 PID: 5071 Comm: syz-executor263 Not tainted 6.2.0-rc1-syzkaller #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 10/26/2022
RIP: 0010:__alloc_pages+0x30a/0x560 mm/page_alloc.c:5525
RSP: 0018:ffffc90003c2f1c0 EFLAGS: 00010246
RAX: ffffc90003c2f220 RBX: 0000000000000014 RCX: 0000000000000000
RDX: 0000000000000028 RSI: 0000000000000000 RDI: ffffc90003c2f248
RBP: ffffc90003c2f2d8 R08: dffffc0000000000 R09: ffffc90003c2f220
R10: fffff52000785e49 R11: 1ffff92000785e44 R12: 0000000000040d40
R13: 1ffff92000785e40 R14: dffffc0000000000 R15: 1ffff92000785e3c
FS:  0000555556c0d300(0000) GS:ffff8880b9800000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 00007f95d5e04138 CR3: 00000000793aa000 CR4: 00000000003506f0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
Call Trace:
 <TASK>
 __alloc_pages_node include/linux/gfp.h:237 [inline]
 alloc_pages_node include/linux/gfp.h:260 [inline]
 __kmalloc_large_node+0x95/0x1e0 mm/slab_common.c:1113
 __do_kmalloc_node mm/slab_common.c:956 [inline]
 __kmalloc+0xfe/0x190 mm/slab_common.c:981
 kmalloc include/linux/slab.h:584 [inline]
 kzalloc include/linux/slab.h:720 [inline]
 ext4_update_inline_data+0x236/0x6b0 fs/ext4/inline.c:346
 ext4_update_inline_dir fs/ext4/inline.c:1115 [inline]
 ext4_try_add_inline_entry+0x328/0x990 fs/ext4/inline.c:1307
 ext4_add_entry+0x5a4/0xeb0 fs/ext4/namei.c:2385
 ext4_add_nondir+0x96/0x260 fs/ext4/namei.c:2772
 ext4_create+0x36c/0x560 fs/ext4/namei.c:2817
 lookup_open fs/namei.c:3413 [inline]
 open_last_lookups fs/namei.c:3481 [inline]
 path_openat+0x12ac/0x2dd0 fs/namei.c:3711
 do_filp_open+0x264/0x4f0 fs/namei.c:3741
 do_sys_openat2+0x124/0x4e0 fs/open.c:1310
 do_sys_open fs/open.c:1326 [inline]
 __do_sys_openat fs/open.c:1342 [inline]
 __se_sys_openat fs/open.c:1337 [inline]
 __x64_sys_openat+0x243/0x290 fs/open.c:1337
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

Above issue happens as follows:
ext4_iget
   ext4_find_inline_data_nolock ->i_inline_off=164 i_inline_size=60
ext4_try_add_inline_entry
   __ext4_mark_inode_dirty
      ext4_expand_extra_isize_ea ->i_extra_isize=32 s_want_extra_isize=44
         ext4_xattr_shift_entries
	 ->after shift i_inline_off is incorrect, actually is change to 176
ext4_try_add_inline_entry
  ext4_update_inline_dir
    get_max_inline_xattr_value_size
      if (EXT4_I(inode)->i_inline_off)
	entry = (struct ext4_xattr_entry *)((void *)raw_inode +
			EXT4_I(inode)->i_inline_off);
        free += EXT4_XATTR_SIZE(le32_to_cpu(entry->e_value_size));
	->As entry is incorrect, then 'free' may be negative
   ext4_update_inline_data
      value = kzalloc(len, GFP_NOFS);
      -> len is unsigned int, maybe very large, then trigger warning when
         'kzalloc()'

To resolve the above issue we need to update 'i_inline_off' after
'ext4_xattr_shift_entries()'.  We do not need to set
EXT4_STATE_MAY_INLINE_DATA flag here, since ext4_mark_inode_dirty()
already sets this flag if needed.  Setting EXT4_STATE_MAY_INLINE_DATA
when it is needed may trigger a BUG_ON in ext4_writepages().

## References
- https://git.kernel.org/stable/c/2b96b4a5d9443ca4cad58b0040be455803c05a42
- https://git.kernel.org/stable/c/35161cec76772f74526f5886ad4082ec48511d5c
- https://git.kernel.org/stable/c/39c5df2ca544368b44b59d0f6d80131e90763371
- https://git.kernel.org/stable/c/74d775083e9f3d9dadf9e3b5f3e0028d1ad0bd5c
- https://git.kernel.org/stable/c/92eee6a82a9a6f9f83559e17a2b6b935e1a5cd25
- https://git.kernel.org/stable/c/a9bd94f67b27739bbe8583c52256502bd4cc7e83
- https://git.kernel.org/stable/c/c5aa102b433b1890e1ccaa40c06826c77dda1665
- https://git.kernel.org/stable/c/ca500cf2eceb5a8e93bf71ab97b5f7a18ecabce2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53100.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
