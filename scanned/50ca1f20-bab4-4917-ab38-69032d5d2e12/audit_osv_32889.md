# [H] media: vidtv: Terminating the subsequent process of initialization failure

## Summary
Severity: High
Advisory: CVE-2025-38227
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38227
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: vidtv: Terminating the subsequent process of initialization failure

syzbot reported a slab-use-after-free Read in vidtv_mux_init. [1]

After PSI initialization fails, the si member is accessed again, resulting
in this uaf.

After si initialization fails, the subsequent process needs to be exited.

[1]
BUG: KASAN: slab-use-after-free in vidtv_mux_pid_ctx_init drivers/media/test-drivers/vidtv/vidtv_mux.c:78 [inline]
BUG: KASAN: slab-use-after-free in vidtv_mux_init+0xac2/0xbe0 drivers/media/test-drivers/vidtv/vidtv_mux.c:524
Read of size 8 at addr ffff88802fa42acc by task syz.2.37/6059

CPU: 0 UID: 0 PID: 6059 Comm: syz.2.37 Not tainted 6.14.0-rc5-syzkaller #0
Hardware name: Google Compute Engine, BIOS Google 02/12/2025
Call Trace:
<TASK>
__dump_stack lib/dump_stack.c:94 [inline]
dump_stack_lvl+0x116/0x1f0 lib/dump_stack.c:120
print_address_description mm/kasan/report.c:408 [inline]
print_report+0xc3/0x670 mm/kasan/report.c:521
kasan_report+0xd9/0x110 mm/kasan/report.c:634
vidtv_mux_pid_ctx_init drivers/media/test-drivers/vidtv/vidtv_mux.c:78
vidtv_mux_init+0xac2/0xbe0 drivers/media/test-drivers/vidtv/vidtv_mux.c:524
vidtv_start_streaming drivers/media/test-drivers/vidtv/vidtv_bridge.c:194
vidtv_start_feed drivers/media/test-drivers/vidtv/vidtv_bridge.c:239
dmx_section_feed_start_filtering drivers/media/dvb-core/dvb_demux.c:973
dvb_dmxdev_feed_start drivers/media/dvb-core/dmxdev.c:508 [inline]
dvb_dmxdev_feed_restart.isra.0 drivers/media/dvb-core/dmxdev.c:537
dvb_dmxdev_filter_stop+0x2b4/0x3a0 drivers/media/dvb-core/dmxdev.c:564
dvb_dmxdev_filter_free drivers/media/dvb-core/dmxdev.c:840 [inline]
dvb_demux_release+0x92/0x550 drivers/media/dvb-core/dmxdev.c:1246
__fput+0x3ff/0xb70 fs/file_table.c:464
task_work_run+0x14e/0x250 kernel/task_work.c:227
exit_task_work include/linux/task_work.h:40 [inline]
do_exit+0xad8/0x2d70 kernel/exit.c:938
do_group_exit+0xd3/0x2a0 kernel/exit.c:1087
__do_sys_exit_group kernel/exit.c:1098 [inline]
__se_sys_exit_group kernel/exit.c:1096 [inline]
__x64_sys_exit_group+0x3e/0x50 kernel/exit.c:1096
x64_sys_call+0x151f/0x1720 arch/x86/include/generated/asm/syscalls_64.h:232
do_syscall_x64 arch/x86/entry/common.c:52 [inline]
do_syscall_64+0xcd/0x250 arch/x86/entry/common.c:83
entry_SYSCALL_64_after_hwframe+0x77/0x7f
RIP: 0033:0x7f871d58d169
Code: Unable to access opcode bytes at 0x7f871d58d13f.
RSP: 002b:00007fff4b19a788 EFLAGS: 00000246 ORIG_RAX: 00000000000000e7
RAX: ffffffffffffffda RBX: 0000000000000000 RCX: 00007f871d58d169
RDX: 0000000000000064 RSI: 0000000000000000 RDI: 0000000000000000
RBP: 00007fff4b19a7ec R08: 0000000b4b19a87f R09: 00000000000927c0
R10: 0000000000000001 R11: 0000000000000246 R12: 0000000000000003
R13: 00000000000927c0 R14: 000000000001d553 R15: 00007fff4b19a840
 </TASK>

Allocated by task 6059:
 kasan_save_stack+0x33/0x60 mm/kasan/common.c:47
 kasan_save_track+0x14/0x30 mm/kasan/common.c:68
 poison_kmalloc_redzone mm/kasan/common.c:377 [inline]
 __kasan_kmalloc+0xaa/0xb0 mm/kasan/common.c:394
 kmalloc_noprof include/linux/slab.h:901 [inline]
 kzalloc_noprof include/linux/slab.h:1037 [inline]
 vidtv_psi_pat_table_init drivers/media/test-drivers/vidtv/vidtv_psi.c:970
 vidtv_channel_si_init drivers/media/test-drivers/vidtv/vidtv_channel.c:423
 vidtv_mux_init drivers/media/test-drivers/vidtv/vidtv_mux.c:519
 vidtv_start_streaming drivers/media/test-drivers/vidtv/vidtv_bridge.c:194
 vidtv_start_feed drivers/media/test-drivers/vidtv/vidtv_bridge.c:239
 dmx_section_feed_start_filtering drivers/media/dvb-core/dvb_demux.c:973
 dvb_dmxdev_feed_start drivers/media/dvb-core/dmxdev.c:508 [inline]
 dvb_dmxdev_feed_restart.isra.0 drivers/media/dvb-core/dmxdev.c:537
 dvb_dmxdev_filter_stop+0x2b4/0x3a0 drivers/media/dvb-core/dmxdev.c:564
 dvb_dmxdev_filter_free drivers/media/dvb-core/dmxdev.c:840 [inline]
 dvb_demux_release+0x92/0x550 drivers/media/dvb-core/dmxdev.c:1246
 __fput+0x3ff/0xb70 fs/file_tabl
---truncated---

## References
- https://git.kernel.org/stable/c/1d5f88f053480326873115092bc116b7d14916ba
- https://git.kernel.org/stable/c/685c18bc5a36f823ee725e85aac1303ef5f535ba
- https://git.kernel.org/stable/c/72541cae73d0809a6416bfcd2ee6473046a0013a
- https://git.kernel.org/stable/c/7e62be1f3b241bc9faee547864bb39332955509b
- https://git.kernel.org/stable/c/9824e1732a163e005aa84e12ec439493ebd4f097
- https://git.kernel.org/stable/c/e1d72ff111eceea6b28dccb7ca4e8f4900b11729
- https://git.kernel.org/stable/c/f8c2483be6e8bb6c2148315b4a924c65bb442b5e
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38227.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38227
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
