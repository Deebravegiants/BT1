# [H] net: bridge: mcast: wait for previous gc cycles when removing port

## Summary
Severity: High
Advisory: CVE-2024-44934
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-44934
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.165, >=5.16.0 <6.1.105, >=6.2.0 <6.6.46, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bridge: mcast: wait for previous gc cycles when removing port

syzbot hit a use-after-free[1] which is caused because the bridge doesn't
make sure that all previous garbage has been collected when removing a
port. What happens is:
      CPU 1                   CPU 2
 start gc cycle           remove port
                         acquire gc lock first
 wait for lock
                         call br_multicasg_gc() directly
 acquire lock now but    free port
 the port can be freed
 while grp timers still
 running

Make sure all previous gc cycles have finished by using flush_work before
freeing the port.

[1]
  BUG: KASAN: slab-use-after-free in br_multicast_port_group_expired+0x4c0/0x550 net/bridge/br_multicast.c:861
  Read of size 8 at addr ffff888071d6d000 by task syz.5.1232/9699

  CPU: 1 PID: 9699 Comm: syz.5.1232 Not tainted 6.10.0-rc5-syzkaller-00021-g24ca36a562d6 #0
  Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 06/07/2024
  Call Trace:
   <IRQ>
   __dump_stack lib/dump_stack.c:88 [inline]
   dump_stack_lvl+0x116/0x1f0 lib/dump_stack.c:114
   print_address_description mm/kasan/report.c:377 [inline]
   print_report+0xc3/0x620 mm/kasan/report.c:488
   kasan_report+0xd9/0x110 mm/kasan/report.c:601
   br_multicast_port_group_expired+0x4c0/0x550 net/bridge/br_multicast.c:861
   call_timer_fn+0x1a3/0x610 kernel/time/timer.c:1792
   expire_timers kernel/time/timer.c:1843 [inline]
   __run_timers+0x74b/0xaf0 kernel/time/timer.c:2417
   __run_timer_base kernel/time/timer.c:2428 [inline]
   __run_timer_base kernel/time/timer.c:2421 [inline]
   run_timer_base+0x111/0x190 kernel/time/timer.c:2437

## References
- https://git.kernel.org/stable/c/0d8b26e10e680c01522d7cc14abe04c3265a928f
- https://git.kernel.org/stable/c/1e16828020c674b3be85f52685e8b80f9008f50f
- https://git.kernel.org/stable/c/92c4ee25208d0f35dafc3213cdf355fbe449e078
- https://git.kernel.org/stable/c/b2f794b168cf560682ff976b255aa6d29d14a658
- https://git.kernel.org/stable/c/e3145ca904fa8dbfd1a5bf0187905bc117b0efce
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44934.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44934
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
