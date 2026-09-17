# [H] bpf, sockmap: Fix cork use-after-free in tcp_bpf_sendmsg()

## Summary
Severity: High
Advisory: CVE-2026-68284
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68284
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Fix cork use-after-free in tcp_bpf_sendmsg()

tcp_bpf_sendmsg() keeps msg_tx across sk_stream_wait_memory(), which
drops and reacquires the socket lock.  Its error path tries to decide
whether msg_tx names the local temporary message by comparing it with
the current value of psock->cork.

This comparison is unsafe when two threads send on the same socket:

  Thread A                         Thread B
  msg_tx = psock->cork
  sk_msg_alloc() fails
  sk_stream_wait_memory()
    releases the socket lock      acquires the socket lock
                                  completes the cork
                                  psock->cork = NULL
                                  frees the cork
    reacquires the socket lock
  msg_tx != psock->cork
  sk_msg_free(msg_tx)

The stale cork is therefore mistaken for the local temporary message
and freed again.  KASAN reported:

  BUG: KASAN: slab-use-after-free in sk_msg_free+0x49/0x50
  Read of size 4 at addr ffff88810c908800 by task poc/90
  Call Trace:
   sk_msg_free+0x49/0x50
   tcp_bpf_sendmsg+0x14f5/0x1cc0
   __sys_sendto+0x32c/0x3a0
   __x64_sys_sendto+0xdb/0x1b0
  Allocated by task 89:
   __kasan_kmalloc+0x8f/0xa0
   tcp_bpf_sendmsg+0x16b3/0x1cc0
  Freed by task 91:
   __kasan_slab_free+0x43/0x70
   kfree+0x131/0x3c0
   tcp_bpf_sendmsg+0xec3/0x1cc0

msg_tx can only name the stack-local tmp or the shared cork. Check for
tmp directly so a changed psock->cork cannot turn a shared message into
an apparent local one.

## References
- https://git.kernel.org/stable/c/0688e6fe599d2d39147ae9ece97944c6e1815ebf
- https://git.kernel.org/stable/c/2d66a033864e27ab8d5e44cb36f31d9d2413bee4
- https://git.kernel.org/stable/c/54be47e7cbb936429c3bbdfc526ea943954aaf80
- https://git.kernel.org/stable/c/752b1159ed5d0c48fe169a3721b96660a9822aa1
- https://git.kernel.org/stable/c/786d690257ec7a0c839f8710456e444ce3f1348b
- https://git.kernel.org/stable/c/b2bcbeabfd843d47468fa095b1bd08ddb90cf616
- https://git.kernel.org/stable/c/cde4d6bcd9b73073c66498f6723c7b364c4dbc18
- https://git.kernel.org/stable/c/ee762f684eefa59de34d9ed93cab08336e834f47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68284.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
