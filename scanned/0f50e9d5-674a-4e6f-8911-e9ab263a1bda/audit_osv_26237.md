# [H] UBSAN: array-index-out-of-bounds in dtSplitRoot

## Summary
Severity: High
Advisory: CVE-2023-52603
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52603
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

UBSAN: array-index-out-of-bounds in dtSplitRoot

Syzkaller reported the following issue:

oop0: detected capacity change from 0 to 32768

UBSAN: array-index-out-of-bounds in fs/jfs/jfs_dtree.c:1971:9
index -2 is out of range for type 'struct dtslot [128]'
CPU: 0 PID: 3613 Comm: syz-executor270 Not tainted 6.0.0-syzkaller-09423-g493ffd6605b2 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/22/2022
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x1b1/0x28e lib/dump_stack.c:106
 ubsan_epilogue lib/ubsan.c:151 [inline]
 __ubsan_handle_out_of_bounds+0xdb/0x130 lib/ubsan.c:283
 dtSplitRoot+0x8d8/0x1900 fs/jfs/jfs_dtree.c:1971
 dtSplitUp fs/jfs/jfs_dtree.c:985 [inline]
 dtInsert+0x1189/0x6b80 fs/jfs/jfs_dtree.c:863
 jfs_mkdir+0x757/0xb00 fs/jfs/namei.c:270
 vfs_mkdir+0x3b3/0x590 fs/namei.c:4013
 do_mkdirat+0x279/0x550 fs/namei.c:4038
 __do_sys_mkdirat fs/namei.c:4053 [inline]
 __se_sys_mkdirat fs/namei.c:4051 [inline]
 __x64_sys_mkdirat+0x85/0x90 fs/namei.c:4051
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x63/0xcd
RIP: 0033:0x7fcdc0113fd9
Code: ff ff c3 66 2e 0f 1f 84 00 00 00 00 00 0f 1f 40 00 48 89 f8 48 89 f7 48 89 d6 48 89 ca 4d 89 c2 4d 89 c8 4c 8b 4c 24 08 0f 05 <48> 3d 01 f0 ff ff 73 01 c3 48 c7 c1 c0 ff ff ff f7 d8 64 89 01 48
RSP: 002b:00007ffeb8bc67d8 EFLAGS: 00000246 ORIG_RAX: 0000000000000102
RAX: ffffffffffffffda RBX: 0000000000000000 RCX: 00007fcdc0113fd9
RDX: 0000000000000000 RSI: 0000000020000340 RDI: 0000000000000003
RBP: 00007fcdc00d37a0 R08: 0000000000000000 R09: 00007fcdc00d37a0
R10: 00005555559a72c0 R11: 0000000000000246 R12: 00000000f8008000
R13: 0000000000000000 R14: 00083878000000f8 R15: 0000000000000000
 </TASK>

The issue is caused when the value of fsi becomes less than -1.
The check to break the loop when fsi value becomes -1 is present
but syzbot was able to produce value less than -1 which cause the error.
This patch simply add the change for the values less than 0.

The patch is tested via syzbot.

## References
- https://git.kernel.org/stable/c/27e56f59bab5ddafbcfe69ad7a4a6ea1279c1b16
- https://git.kernel.org/stable/c/6e2902ecc77e9760a9fc447f56d598383e2372d2
- https://git.kernel.org/stable/c/7aa33854477d9c346f5560a1a1fcb3fe7783e2a8
- https://git.kernel.org/stable/c/e30b52a2ea3d1e0aaee68096957cf90a2f4ec5af
- https://git.kernel.org/stable/c/e4cbc857d75d4e22a1f75446e7480b1f305d8d60
- https://git.kernel.org/stable/c/e4ce01c25ccbea02a09a5291c21749b1fc358e39
- https://git.kernel.org/stable/c/edff092a59260bf0b0a2eba219cb3da6372c2f9f
- https://git.kernel.org/stable/c/fd3486a893778770557649fe28afa5e463d4ed07
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52603.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52603
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
