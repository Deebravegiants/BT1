# [H] bpf: tcp: fix double sock release on batch realloc

## Summary
Severity: High
Advisory: CVE-2026-64575
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64575
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: tcp: fix double sock release on batch realloc

bpf_iter_tcp_batch() releases the current batch via
bpf_iter_tcp_put_batch(), which drops the socket refs and rewrites
each slot with the socket cookie, then grows the batch. cur_sk/end_sk
are kept for bpf_iter_tcp_resume(), but on realloc failure the function
returns ERR_PTR() before resume runs, leaving cur_sk < end_sk over
slots that now hold cookies rather than sock pointers.
bpf_iter_tcp_seq_stop() then calls bpf_iter_tcp_put_batch() again and
dereferences a cookie as a struct sock.

Empty the batch on the failure path so stop() does not release it
again. The sockets were already freed by the first
bpf_iter_tcp_put_batch(), so nothing leaks, and a later read() rescans
the bucket from the start instead of skipping it. The sibling
GFP_NOWAIT failure path still holds real socket references and is left
for stop() to release.

  BUG: KASAN: null-ptr-deref in __sock_gen_cookie
  Read of size 8 at addr 0000000000000059 by task exploit
   ...
   __sock_gen_cookie (net/core/sock_diag.c:28)
   bpf_iter_tcp_put_batch (net/ipv4/tcp_ipv4.c:2918)
   bpf_iter_tcp_seq_stop (net/ipv4/tcp_ipv4.c:3270)
   bpf_seq_read (kernel/bpf/bpf_iter.c:205)
   vfs_read (fs/read_write.c:572)
   ksys_read (fs/read_write.c:716)
   do_syscall_64
   entry_SYSCALL_64_after_hwframe
  Kernel panic - not syncing: Fatal exception

## References
- https://git.kernel.org/stable/c/7a6a6d2a127866935f87b55b557bc89693065462
- https://git.kernel.org/stable/c/8a726e9585ffe7bfbfad2b5279277a00973970f3
- https://git.kernel.org/stable/c/980a813452754f8001704744e92f7aa697c53dd3
- https://git.kernel.org/stable/c/9f27c4f0ae35b5390ce4f7a54d3501144e41a54d
- https://git.kernel.org/stable/c/c842882e4c5d2818b858d6baf3fd10958c93f729
- https://git.kernel.org/stable/c/f0c1810320b0dac228103fad7311e89532134d83
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64575.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64575
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
