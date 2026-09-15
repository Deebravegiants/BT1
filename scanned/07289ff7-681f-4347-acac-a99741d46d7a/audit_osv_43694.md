# [H] bpf, sockmap: Fix sk_redir use-after-free in send verdict

## Summary
Severity: High
Advisory: CVE-2026-74589
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74589
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Fix sk_redir use-after-free in send verdict

sk_psock_msg_verdict() takes a socket reference for psock->sk_redir.
tcp_bpf_send_verdict() copies that pointer while holding the source socket
lock, but does not take a reference for the local copy before dropping the
lock around tcp_bpf_sendmsg_redir().

When apply_bytes keeps the cached verdict active, another sendmsg() on the
same source socket can consume the remaining bytes and release the cached
reference while the first thread still holds only the raw local pointer:

  CPU 0                                  CPU 1
  sk_redir = psock->sk_redir
  apply_bytes remains nonzero
  release_sock(sk)
                                         lock_sock(sk)
                                         apply_bytes reaches zero
                                         psock->sk_redir = NULL
                                         release_sock(sk)
                                         tcp_bpf_sendmsg_redir(sk_redir)
                                         sock_put(sk_redir)
  tcp_bpf_sendmsg_redir(sk_redir)

The final sock_put() can free sk_redir before CPU 0 dereferences it.

KASAN reported:

  BUG: KASAN: slab-use-after-free in tcp_bpf_sendmsg_redir+0xf39/0x1020
  Read of size 8 at addr ffff888108537090 by task poc/87
  Call Trace:
   tcp_bpf_sendmsg_redir+0xf39/0x1020
   tcp_bpf_sendmsg+0x977/0x1a50
   __sys_sendto+0x32c/0x3a0
   __x64_sys_sendto+0xdb/0x1b0
  Allocated by task 85:
   sk_prot_alloc+0x56/0x210
   sk_clone+0x6f/0x14b0
   inet_csk_clone_lock+0x24/0x740
   tcp_create_openreq_child+0x25/0x2710
   tcp_v4_syn_recv_sock+0x10a/0xe00
  Freed by task 0:
   __kasan_slab_free+0x43/0x70
   slab_free_after_rcu_debug+0xa6/0x1e0
   rcu_core+0x50a/0x1850
  Last potentially related work creation:
   __sk_destruct+0x3da/0x540
   sk_psock_destroy+0x81e/0xab0
   process_one_work+0x63a/0x1070

Take a temporary socket reference while the source socket lock still
protects psock->sk_redir, and drop it after tcp_bpf_sendmsg_redir()
returns.  This keeps each unlocked use independent of cached-verdict
ownership.

## References
- https://git.kernel.org/stable/c/1cec526cf0a2227395f2c2f4b671cb052ff0b00e
- https://git.kernel.org/stable/c/41b7da0cb72ca5aa1e62b68dab323d0791fc6bdf
- https://git.kernel.org/stable/c/4c9d9aa809c261dc0490a0e19d675f7e8e4c85bf
- https://git.kernel.org/stable/c/90a19b0894ba79a699b48cf44421b36fbd566e99
- https://git.kernel.org/stable/c/9b4fbc371a6ecf1b4e43b5a629015cc0830d8de3
- https://git.kernel.org/stable/c/a14e4ef1d90c3418f01b3b6b8fd3a40a0a208a10
- https://git.kernel.org/stable/c/a76624733730e541e4955fdecf506af2f6b20558
- https://git.kernel.org/stable/c/d192cff2a37d59206dabe6ec2e60ceac6271f274
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74589.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74589
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
