# [H] bpf: Fix UAF in sock clone early bailouts

## Summary
Severity: High
Advisory: CVE-2026-68399
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68399
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix UAF in sock clone early bailouts

Similar to recent commit 9b51a6155d14 ("bpf,fork: wipe ->bpf_storage
before bailouts that access it"), sk_clone() performs an initial
shallow copy of the socket field ->sk_bpf_storage via sock_copy()
for the cloned socket newsk.

If sk_clone() bails out early (e.g. if sk_filter_charge() fails) prior
to calling bpf_sk_storage_clone(), newsk->sk_bpf_storage still points
to the parent socket's BPF local storage. When newsk is subsequently
freed via sk_free(), the deallocation path (__sk_destruct() ->
bpf_sk_storage_free()) destroys the parent socket's BPF local storage,
leading to a use-after-free (UAF) on the parent socket.

Fix this by resetting newsk->sk_bpf_storage to NULL immediately after
sock_copy() in sk_clone(), and remove the now redundant initialization
from bpf_sk_storage_clone().

## References
- https://git.kernel.org/stable/c/14b49b5ab29979552c219a09e569b424fbbf4a6e
- https://git.kernel.org/stable/c/7cbd0c4cebe4c9f678d15e6b9ba975e1155a107f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68399.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68399
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
