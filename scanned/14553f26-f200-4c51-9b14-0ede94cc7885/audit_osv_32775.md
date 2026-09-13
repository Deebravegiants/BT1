# [H] tracing: Fix oob write in trace_seq_to_buffer()

## Summary
Severity: High
Advisory: CVE-2025-37923
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37923
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.182, >=5.16.0 <6.1.138, >=6.2.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Fix oob write in trace_seq_to_buffer()

syzbot reported this bug:
==================================================================
BUG: KASAN: slab-out-of-bounds in trace_seq_to_buffer kernel/trace/trace.c:1830 [inline]
BUG: KASAN: slab-out-of-bounds in tracing_splice_read_pipe+0x6be/0xdd0 kernel/trace/trace.c:6822
Write of size 4507 at addr ffff888032b6b000 by task syz.2.320/7260

CPU: 1 UID: 0 PID: 7260 Comm: syz.2.320 Not tainted 6.15.0-rc1-syzkaller-00301-g3bde70a2c827 #0 PREEMPT(full)
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 02/12/2025
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x116/0x1f0 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:408 [inline]
 print_report+0xc3/0x670 mm/kasan/report.c:521
 kasan_report+0xe0/0x110 mm/kasan/report.c:634
 check_region_inline mm/kasan/generic.c:183 [inline]
 kasan_check_range+0xef/0x1a0 mm/kasan/generic.c:189
 __asan_memcpy+0x3c/0x60 mm/kasan/shadow.c:106
 trace_seq_to_buffer kernel/trace/trace.c:1830 [inline]
 tracing_splice_read_pipe+0x6be/0xdd0 kernel/trace/trace.c:6822
 ....
==================================================================

It has been reported that trace_seq_to_buffer() tries to copy more data
than PAGE_SIZE to buf. Therefore, to prevent this, we should use the
smaller of trace_seq_used(&iter->seq) and PAGE_SIZE as an argument.

## References
- https://git.kernel.org/stable/c/056ebbddb8faf4ddf83d005454dd78fc25c2d897
- https://git.kernel.org/stable/c/1a3f9482b50b74fa9421bff8ceecfefd0dc06f8f
- https://git.kernel.org/stable/c/1f27a3e93b8d674b24b27fcdbc6f72743cd96c0d
- https://git.kernel.org/stable/c/441021e5b3c7d9bd1b963590652c415929f3b157
- https://git.kernel.org/stable/c/665ce421041890571852422487f4c613d1824ba9
- https://git.kernel.org/stable/c/c5d2b66c5ef5037b4b4360e5447605ff00ba1bd4
- https://git.kernel.org/stable/c/f4b0174e9f18aaba59ee6ffdaf8827a7f94eb606
- https://git.kernel.org/stable/c/f5178c41bb43444a6008150fe6094497135d07cb
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37923.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37923
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
