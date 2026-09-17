# [H] udf: Fix a slab-out-of-bounds write bug in udf_find_entry()

## Summary
Severity: High
Advisory: CVE-2022-49846
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49846
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

udf: Fix a slab-out-of-bounds write bug in udf_find_entry()

Syzbot reported a slab-out-of-bounds Write bug:

loop0: detected capacity change from 0 to 2048
==================================================================
BUG: KASAN: slab-out-of-bounds in udf_find_entry+0x8a5/0x14f0
fs/udf/namei.c:253
Write of size 105 at addr ffff8880123ff896 by task syz-executor323/3610

CPU: 0 PID: 3610 Comm: syz-executor323 Not tainted
6.1.0-rc2-syzkaller-00105-gb229b6ca5abb #0
Hardware name: Google Compute Engine/Google Compute Engine, BIOS
Google 10/11/2022
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x1b1/0x28e lib/dump_stack.c:106
 print_address_description+0x74/0x340 mm/kasan/report.c:284
 print_report+0x107/0x1f0 mm/kasan/report.c:395
 kasan_report+0xcd/0x100 mm/kasan/report.c:495
 kasan_check_range+0x2a7/0x2e0 mm/kasan/generic.c:189
 memcpy+0x3c/0x60 mm/kasan/shadow.c:66
 udf_find_entry+0x8a5/0x14f0 fs/udf/namei.c:253
 udf_lookup+0xef/0x340 fs/udf/namei.c:309
 lookup_open fs/namei.c:3391 [inline]
 open_last_lookups fs/namei.c:3481 [inline]
 path_openat+0x10e6/0x2df0 fs/namei.c:3710
 do_filp_open+0x264/0x4f0 fs/namei.c:3740
 do_sys_openat2+0x124/0x4e0 fs/open.c:1310
 do_sys_open fs/open.c:1326 [inline]
 __do_sys_creat fs/open.c:1402 [inline]
 __se_sys_creat fs/open.c:1396 [inline]
 __x64_sys_creat+0x11f/0x160 fs/open.c:1396
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd
RIP: 0033:0x7ffab0d164d9
Code: ff ff c3 66 2e 0f 1f 84 00 00 00 00 00 0f 1f 40 00 48 89 f8 48 89
f7 48 89 d6 48 89 ca 4d 89 c2 4d 89 c8 4c 8b 4c 24 08 0f 05 <48> 3d 01
f0 ff ff 73 01 c3 48 c7 c1 c0 ff ff ff f7 d8 64 89 01 48
RSP: 002b:00007ffe1a7e6bb8 EFLAGS: 00000246 ORIG_RAX: 0000000000000055
RAX: ffffffffffffffda RBX: 0000000000000000 RCX: 00007ffab0d164d9
RDX: 00007ffab0d164d9 RSI: 0000000000000000 RDI: 0000000020000180
RBP: 00007ffab0cd5a10 R08: 0000000000000000 R09: 0000000000000000
R10: 00005555573552c0 R11: 0000000000000246 R12: 00007ffab0cd5aa0
R13: 0000000000000000 R14: 0000000000000000 R15: 0000000000000000
 </TASK>

Allocated by task 3610:
 kasan_save_stack mm/kasan/common.c:45 [inline]
 kasan_set_track+0x3d/0x60 mm/kasan/common.c:52
 ____kasan_kmalloc mm/kasan/common.c:371 [inline]
 __kasan_kmalloc+0x97/0xb0 mm/kasan/common.c:380
 kmalloc include/linux/slab.h:576 [inline]
 udf_find_entry+0x7b6/0x14f0 fs/udf/namei.c:243
 udf_lookup+0xef/0x340 fs/udf/namei.c:309
 lookup_open fs/namei.c:3391 [inline]
 open_last_lookups fs/namei.c:3481 [inline]
 path_openat+0x10e6/0x2df0 fs/namei.c:3710
 do_filp_open+0x264/0x4f0 fs/namei.c:3740
 do_sys_openat2+0x124/0x4e0 fs/open.c:1310
 do_sys_open fs/open.c:1326 [inline]
 __do_sys_creat fs/open.c:1402 [inline]
 __se_sys_creat fs/open.c:1396 [inline]
 __x64_sys_creat+0x11f/0x160 fs/open.c:1396
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

The buggy address belongs to the object at ffff8880123ff800
 which belongs to the cache kmalloc-256 of size 256
The buggy address is located 150 bytes inside of
 256-byte region [ffff8880123ff800, ffff8880123ff900)

The buggy address belongs to the physical page:
page:ffffea000048ff80 refcount:1 mapcount:0 mapping:0000000000000000
index:0x0 pfn:0x123fe
head:ffffea000048ff80 order:1 compound_mapcount:0 compound_pincount:0
flags: 0xfff00000010200(slab|head|node=0|zone=1|lastcpupid=0x7ff)
raw: 00fff00000010200 ffffea00004b8500 dead000000000003 ffff888012041b40
raw: 0000000000000000 0000000080100010 00000001ffffffff 0000000000000000
page dumped because: kasan: bad access detected
page_owner tracks the page as allocated
page last allocated via order 0, migratetype Unmovable, gfp_mask 0x0(),
pid 1, tgid 1 (swapper/0), ts 1841222404, free_ts 0
 create_dummy_stack mm/page_owner.c:
---truncated---

## References
- https://git.kernel.org/stable/c/03f9582a6a2ebd25a440896475c968428c4b63e7
- https://git.kernel.org/stable/c/583fdd98d94acba1e7225e5cc29063aef0741030
- https://git.kernel.org/stable/c/7a6051d734f1ed0031e2216f9a538621235c11a4
- https://git.kernel.org/stable/c/ac79001b8e603226fab17240a79cb9ef679d3cd9
- https://git.kernel.org/stable/c/c736ed8541605e3a25075bb1cbf8f38cb3083238
- https://git.kernel.org/stable/c/c8af247de385ce49afabc3bf1cf4fd455c94bfe8
- https://git.kernel.org/stable/c/d8971f410739a864c537e0ac29344a7b6c450232
- https://git.kernel.org/stable/c/f1517721c408631f09d54c743aa70cb07fd3eebd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49846.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49846
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
