# [H] net: fix out-of-bounds access in ops_init

## Summary
Severity: High
Advisory: CVE-2024-36883
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36883
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fix out-of-bounds access in ops_init

net_alloc_generic is called by net_alloc, which is called without any
locking. It reads max_gen_ptrs, which is changed under pernet_ops_rwsem. It
is read twice, first to allocate an array, then to set s.len, which is
later used to limit the bounds of the array access.

It is possible that the array is allocated and another thread is
registering a new pernet ops, increments max_gen_ptrs, which is then used
to set s.len with a larger than allocated length for the variable array.

Fix it by reading max_gen_ptrs only once in net_alloc_generic. If
max_gen_ptrs is later incremented, it will be caught in net_assign_generic.

## References
- https://git.kernel.org/stable/c/0c3248bc708a7797be573214065cf908ff1f54c7
- https://git.kernel.org/stable/c/2d60ff5874aefd006717ca5e22ac1e25eac29c42
- https://git.kernel.org/stable/c/3cdc34d76c4f777579e28ad373979d36c030cfd3
- https://git.kernel.org/stable/c/7b0e64583eab8c1d896b47e5dd0bf2e7d86ec41f
- https://git.kernel.org/stable/c/9518b79bfd2fbf99fa9b7e8e36bcb1825e7ba030
- https://git.kernel.org/stable/c/a26ff37e624d12e28077e5b24d2b264f62764ad6
- https://git.kernel.org/stable/c/b6dbfd5bcc267a95a0bf1bf96af46243f96ec6cd
- https://git.kernel.org/stable/c/f4f94587e1bf87cb40ec33955a9d90148dd026ab
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36883.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36883
- https://security.netapp.com/advisory/ntap-20241018-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
