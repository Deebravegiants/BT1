# [H] bpf, sockmap: fix integer overflow in bpf_msg_pop_data() bounds check

## Summary
Severity: High
Advisory: CVE-2026-74256
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74256
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: fix integer overflow in bpf_msg_pop_data() bounds check

start and len are u32, so

	u64 last = start + len;

evaluates start + len in 32-bit and wraps before storing it in last.
The bounds check

	if (start >= offset + l || last > msg->sg.size)
		return -EINVAL;

can then be passed with an out-of-range start/len, after which the pop
loop runs off the end of the scatterlist and sk_msg_shift_left() calls
put_page() on the empty msg->sg.end slot:

  Oops: general protection fault, probably for non-canonical address
  0xdffffc0000000001: 0000 [#1] SMP KASAN PTI
  KASAN: null-ptr-deref in range [0x0000000000000008-0x000000000000000f]
  RIP: 0010:sk_msg_shift_left net/core/filter.c:2957 [inline]
  RIP: 0010:____bpf_msg_pop_data net/core/filter.c:3103 [inline]
  RIP: 0010:bpf_msg_pop_data+0x753/0x1a10 net/core/filter.c:2984
  Call Trace:
   <TASK>
   bpf_prog_4cc92c278f4d5d56+0x1b1/0x1e8
   bpf_prog_run_pin_on_cpu+0x107/0x320 include/linux/filter.h:746
   sk_psock_msg_verdict+0x357/0x7f0 net/core/skmsg.c:934
   tcp_bpf_send_verdict net/ipv4/tcp_bpf.c:420 [inline]
   tcp_bpf_sendmsg+0x766/0x1ae0 net/ipv4/tcp_bpf.c:583
   __sock_sendmsg+0x153/0x1c0 net/socket.c:802
   __sys_sendto+0x326/0x430 net/socket.c:2265
   __x64_sys_sendto+0xe3/0x100 net/socket.c:2268
   do_syscall_64+0x14c/0x480
   entry_SYSCALL_64_after_hwframe+0x77/0x7f
   </TASK>

Widen the addition with a (u64) cast so the bound is evaluated in
64-bit and a len near U32_MAX no longer wraps below msg->sg.size.

While here, change pop from int to u32. It counts bytes against the
unsigned scatterlist lengths and can never be negative, so the signed
type only invites sign-confusion in the pop loop.

## References
- https://git.kernel.org/stable/c/17eb9832a10db2f7a80cb429ca2bc5038445a943
- https://git.kernel.org/stable/c/9ef44ed6fb0c1db01cfcc3de432a33e719713eb5
- https://git.kernel.org/stable/c/a48802fb2cd2d1e23651989f8ff4d15e9d5dad54
- https://git.kernel.org/stable/c/ba5cc05dae8fce237d191c7ea96b1107a791e548
- https://git.kernel.org/stable/c/c05a0ec1cdced622a1a0c7d85679fe02f31033ec
- https://git.kernel.org/stable/c/d693c5ed67dabe1ccbf8dcea93075bdc9ffd4ca0
- https://git.kernel.org/stable/c/e09f7bd7273928b4089e6b71f8e992f2b356ca1b
- https://git.kernel.org/stable/c/fe09dd288722f1c749b7506c0b3e7841a7d85027
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74256.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74256
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
