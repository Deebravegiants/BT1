# [H] bpf, sockmap: Take state lock for af_unix iter

## Summary
Severity: High
Advisory: CVE-2026-53033
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53033
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Take state lock for af_unix iter

When a BPF iterator program updates a sockmap, there is a race condition in
unix_stream_bpf_update_proto() where the `peer` pointer can become stale[1]
during a state transition TCP_ESTABLISHED -> TCP_CLOSE.

        CPU0 bpf                          CPU1 close
        --------                          ----------
// unix_stream_bpf_update_proto()
sk_pair = unix_peer(sk)
if (unlikely(!sk_pair))
   return -EINVAL;
                                     // unix_release_sock()
                                     skpair = unix_peer(sk);
                                     unix_peer(sk) = NULL;
                                     sock_put(skpair)
sock_hold(sk_pair) // UaF

More practically, this fix guarantees that the iterator program is
consistently provided with a unix socket that remains stable during
iterator execution.

[1]:
BUG: KASAN: slab-use-after-free in unix_stream_bpf_update_proto+0x155/0x490
Write of size 4 at addr ffff8881178c9a00 by task test_progs/2231
Call Trace:
 dump_stack_lvl+0x5d/0x80
 print_report+0x170/0x4f3
 kasan_report+0xe4/0x1c0
 kasan_check_range+0x125/0x200
 unix_stream_bpf_update_proto+0x155/0x490
 sock_map_link+0x71c/0xec0
 sock_map_update_common+0xbc/0x600
 sock_map_update_elem+0x19a/0x1f0
 bpf_prog_bbbf56096cdd4f01_selective_dump_unix+0x20c/0x217
 bpf_iter_run_prog+0x21e/0xae0
 bpf_iter_unix_seq_show+0x1e0/0x2a0
 bpf_seq_read+0x42c/0x10d0
 vfs_read+0x171/0xb20
 ksys_read+0xff/0x200
 do_syscall_64+0xf7/0x5e0
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

Allocated by task 2236:
 kasan_save_stack+0x30/0x50
 kasan_save_track+0x14/0x30
 __kasan_slab_alloc+0x63/0x80
 kmem_cache_alloc_noprof+0x1d5/0x680
 sk_prot_alloc+0x59/0x210
 sk_alloc+0x34/0x470
 unix_create1+0x86/0x8a0
 unix_stream_connect+0x318/0x15b0
 __sys_connect+0xfd/0x130
 __x64_sys_connect+0x72/0xd0
 do_syscall_64+0xf7/0x5e0
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

Freed by task 2236:
 kasan_save_stack+0x30/0x50
 kasan_save_track+0x14/0x30
 kasan_save_free_info+0x3b/0x70
 __kasan_slab_free+0x47/0x70
 kmem_cache_free+0x11c/0x590
 __sk_destruct+0x432/0x6e0
 unix_release_sock+0x9b3/0xf60
 unix_release+0x8a/0xf0
 __sock_release+0xb0/0x270
 sock_close+0x18/0x20
 __fput+0x36e/0xac0
 fput_close_sync+0xe5/0x1a0
 __x64_sys_close+0x7d/0xd0
 do_syscall_64+0xf7/0x5e0
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

## References
- https://git.kernel.org/stable/c/1a59cc6b65fd3ad9915aae5970d859109d4ce9fb
- https://git.kernel.org/stable/c/64c2f93fc3254d3bf5de4445fb732ee5c451edb6
- https://git.kernel.org/stable/c/921920c34cb591947dd30c692500795a69f1e3fa
- https://git.kernel.org/stable/c/98f744d204e5d6fca589cd2c44c3190a0c71697f
- https://git.kernel.org/stable/c/c6f4015eac2e3cbc3cb7a17539e10bbb5c2049c3
- https://git.kernel.org/stable/c/d0d124dbcef9318e326956137b31671407094bd4
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53033.json
- https://access.redhat.com/security/cve/CVE-2026-53033
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53033.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53033
- https://bugzilla.redhat.com/show_bug.cgi?id=2492281
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
