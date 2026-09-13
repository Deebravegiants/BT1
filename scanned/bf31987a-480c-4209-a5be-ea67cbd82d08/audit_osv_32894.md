# [H] af_unix: Don't leave consecutive consumed OOB skbs.

## Summary
Severity: High
Advisory: CVE-2025-38236
Aliases: A-432753641, ASB-A-432753641
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-08
Source: https://osv.dev/vulnerability/CVE-2025-38236
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.194, >=5.16.0 <6.1.143, >=6.2.0 <6.6.96, >=6.7.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_unix: Don't leave consecutive consumed OOB skbs.

Jann Horn reported a use-after-free in unix_stream_read_generic().

The following sequences reproduce the issue:

  $ python3
  from socket import *
  s1, s2 = socketpair(AF_UNIX, SOCK_STREAM)
  s1.send(b'x', MSG_OOB)
  s2.recv(1, MSG_OOB)     # leave a consumed OOB skb
  s1.send(b'y', MSG_OOB)
  s2.recv(1, MSG_OOB)     # leave a consumed OOB skb
  s1.send(b'z', MSG_OOB)
  s2.recv(1)              # recv 'z' illegally
  s2.recv(1, MSG_OOB)     # access 'z' skb (use-after-free)

Even though a user reads OOB data, the skb holding the data stays on
the recv queue to mark the OOB boundary and break the next recv().

After the last send() in the scenario above, the sk2's recv queue has
2 leading consumed OOB skbs and 1 real OOB skb.

Then, the following happens during the next recv() without MSG_OOB

  1. unix_stream_read_generic() peeks the first consumed OOB skb
  2. manage_oob() returns the next consumed OOB skb
  3. unix_stream_read_generic() fetches the next not-yet-consumed OOB skb
  4. unix_stream_read_generic() reads and frees the OOB skb

, and the last recv(MSG_OOB) triggers KASAN splat.

The 3. above occurs because of the SO_PEEK_OFF code, which does not
expect unix_skb_len(skb) to be 0, but this is true for such consumed
OOB skbs.

  while (skip >= unix_skb_len(skb)) {
    skip -= unix_skb_len(skb);
    skb = skb_peek_next(skb, &sk->sk_receive_queue);
    ...
  }

In addition to this use-after-free, there is another issue that
ioctl(SIOCATMARK) does not function properly with consecutive consumed
OOB skbs.

So, nothing good comes out of such a situation.

Instead of complicating manage_oob(), ioctl() handling, and the next
ECONNRESET fix by introducing a loop for consecutive consumed OOB skbs,
let's not leave such consecutive OOB unnecessarily.

Now, while receiving an OOB skb in unix_stream_recv_urg(), if its
previous skb is a consumed OOB skb, it is freed.

[0]:
BUG: KASAN: slab-use-after-free in unix_stream_read_actor (net/unix/af_unix.c:3027)
Read of size 4 at addr ffff888106ef2904 by task python3/315

CPU: 2 UID: 0 PID: 315 Comm: python3 Not tainted 6.16.0-rc1-00407-gec315832f6f9 #8 PREEMPT(voluntary)
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-4.fc42 04/01/2014
Call Trace:
 <TASK>
 dump_stack_lvl (lib/dump_stack.c:122)
 print_report (mm/kasan/report.c:409 mm/kasan/report.c:521)
 kasan_report (mm/kasan/report.c:636)
 unix_stream_read_actor (net/unix/af_unix.c:3027)
 unix_stream_read_generic (net/unix/af_unix.c:2708 net/unix/af_unix.c:2847)
 unix_stream_recvmsg (net/unix/af_unix.c:3048)
 sock_recvmsg (net/socket.c:1063 (discriminator 20) net/socket.c:1085 (discriminator 20))
 __sys_recvfrom (net/socket.c:2278)
 __x64_sys_recvfrom (net/socket.c:2291 (discriminator 1) net/socket.c:2287 (discriminator 1) net/socket.c:2287 (discriminator 1))
 do_syscall_64 (arch/x86/entry/syscall_64.c:63 (discriminator 1) arch/x86/entry/syscall_64.c:94 (discriminator 1))
 entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:130)
RIP: 0033:0x7f8911fcea06
Code: 5d e8 41 8b 93 08 03 00 00 59 5e 48 83 f8 fc 75 19 83 e2 39 83 fa 08 75 11 e8 26 ff ff ff 66 0f 1f 44 00 00 48 8b 45 10 0f 05 <48> 8b 5d f8 c9 c3 0f 1f 40 00 f3 0f 1e fa 55 48 89 e5 48 83 ec 08
RSP: 002b:00007fffdb0dccb0 EFLAGS: 00000202 ORIG_RAX: 000000000000002d
RAX: ffffffffffffffda RBX: 00007fffdb0dcdc8 RCX: 00007f8911fcea06
RDX: 0000000000000001 RSI: 00007f8911a5e060 RDI: 0000000000000006
RBP: 00007fffdb0dccd0 R08: 0000000000000000 R09: 0000000000000000
R10: 0000000000000001 R11: 0000000000000202 R12: 00007f89119a7d20
R13: ffffffffc4653600 R14: 0000000000000000 R15: 0000000000000000
 </TASK>

Allocated by task 315:
 kasan_save_stack (mm/kasan/common.c:48)
 kasan_save_track (mm/kasan/common.c:60 (discriminator 1) mm/kasan/common.c:69 (discriminator 1))
 __kasan_slab_alloc (mm/kasan/common.c:348)
 kmem_cache_alloc_
---truncated---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/32ca245464e1479bfea8592b9db227fdc1641705
- https://git.kernel.org/stable/c/523edfed4f68b7794d85b9ac828c5f8f4442e4c5
- https://git.kernel.org/stable/c/61a9ad7b69ce688697e5f63332f03e17725353bc
- https://git.kernel.org/stable/c/8db4d2d026e6e3649832bfe23b96c4acff0756db
- https://git.kernel.org/stable/c/a12237865b48a73183df252029ff5065d73d305e
- https://git.kernel.org/stable/c/fad0a2c16062ac7c606b93166a7ce9d265bab976
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://project-zero.issues.chromium.org/issues/423023990
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38236.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38236
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
