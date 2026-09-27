# [H] net/tcp-ao: fix use-after-free of key in del_async path

## Summary
Severity: High
Advisory: CVE-2026-53389
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53389
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tcp-ao: fix use-after-free of key in del_async path

In tcp_ao_delete_key(), the del_async path skips the current_key
and rnext_key validity checks present in the synchronous path,
assuming these pointers are always NULL on LISTEN sockets.  However,
if a key was added with set_current=1/set_rnext=1 while the socket
was in CLOSE state, current_key and rnext_key will be non-NULL
after listen() transitions the socket to LISTEN.

When such a key is deleted with del_async=1, hlist_del_rcu() and
call_rcu() free the key without clearing the dangling pointers.
After the RCU grace period, getsockopt(TCP_AO_INFO) dereferences
current_key->sndid and rnext_key->rcvid from freed slab memory.

Clear current_key and rnext_key in the del_async path when they
reference the key being deleted.

## References
- https://git.kernel.org/stable/c/5ba9950bc9078e19b69cca1e56d1553b125c6857
- https://git.kernel.org/stable/c/6ce7ef41743740ce15c2061561b784148b565b3f
- https://git.kernel.org/stable/c/7ddc29a094d96e9b3aa280433c6dc443df9eabf2
- https://git.kernel.org/stable/c/e77fbefd1269b5c123e7c651a1ebdce1b87d19a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53389.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
