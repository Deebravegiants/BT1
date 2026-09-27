# [H] bpf, sockmap: reject overflowing copy + len in bpf_msg_push_data()

## Summary
Severity: High
Advisory: CVE-2026-64548
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64548
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: reject overflowing copy + len in bpf_msg_push_data()

When the scatterlist ring is full or nearly full, bpf_msg_push_data()
enters a copy fallback path and computes copy + len for the page
allocation size. Since len comes from BPF with arg3_type = ARG_ANYTHING
and both are u32, a crafted len can wrap the sum to a small value,
causing an undersized allocation followed by an out-of-bounds memcpy.

 BUG: unable to handle page fault for address: ffffed104089a402
 Oops: Oops: 0000 [#1] SMP KASAN NOPTI
 Call Trace:
  __asan_memcpy (mm/kasan/shadow.c:105)
  bpf_msg_push_data (net/core/filter.c:2852 net/core/filter.c:2788)
  bpf_prog_9ed8b5711920a7d7+0x2e/0x36
  sk_psock_msg_verdict (net/core/skmsg.c:934)
  tcp_bpf_sendmsg (net/ipv4/tcp_bpf.c:421 net/ipv4/tcp_bpf.c:584)
  __sys_sendto (net/socket.c:2206)
  do_syscall_64 (arch/x86/entry/syscall_64.c:94)
  entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:130)

Add an overflow check before the allocation.

## References
- https://git.kernel.org/stable/c/0c0a8ed85349dae298712d79cb276acfeb794d82
- https://git.kernel.org/stable/c/4e40056bb5c829f0423f0a6694a0477726d2147e
- https://git.kernel.org/stable/c/888706a76286c547bd035432602571e8024b5305
- https://git.kernel.org/stable/c/a12b1575f9feabd91695a9e9d004862f7195fa25
- https://git.kernel.org/stable/c/bd004716ba75fed6d185795c85cdc92540ebeaab
- https://git.kernel.org/stable/c/db77b6bb6e6edb79b10b4efcce346eec5582d588
- https://git.kernel.org/stable/c/f1644c9508d24f50dd9e8ebe8d3ba86e0996d2f5
- https://git.kernel.org/stable/c/ff39d0e3b4feeb65ca43c453d7c75fdf872ded0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64548.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64548
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
