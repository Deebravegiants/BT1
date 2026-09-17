# [H] net/af_iucv: fix NULL deref in afiucv_hs_callback_syn()

## Summary
Severity: High
Advisory: CVE-2026-68141
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68141
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/af_iucv: fix NULL deref in afiucv_hs_callback_syn()

afiucv_hs_callback_syn() allocates the child socket with GFP_ATOMIC.
If the allocation fails, nsk is NULL.

The connection-refused path is entered when the listen state check
fails, the accept backlog is full, or nsk is NULL. The code
unconditionally calls iucv_sock_kill(nsk) in that path.

iucv_sock_kill() does not accept a NULL socket pointer and immediately
dereferences sk via sock_flag(sk, SOCK_ZAPPED). When nsk is NULL,
calling iucv_sock_kill(nsk) results in a NULL pointer dereference.

Only call iucv_sock_kill() when a child socket was successfully
allocated.

## References
- https://git.kernel.org/stable/c/07e21deb3664001995e0a456dd627ab7dbe127ec
- https://git.kernel.org/stable/c/0e857185591fe79934427c9c0c1c31dc776be134
- https://git.kernel.org/stable/c/33736ff5e7c97d3348ce812e8bd2e125d840743c
- https://git.kernel.org/stable/c/46453b16f38ec7147351f7447e2aec6ea330f7b3
- https://git.kernel.org/stable/c/47a5116e56a6b6fe1e909f244e39cd0fc26ceee4
- https://git.kernel.org/stable/c/6a1eb5b46c19073f8153b7e2c19b408cf353aaf1
- https://git.kernel.org/stable/c/8bb111f87ded6acb9837ec9b45d6f02cda94c51f
- https://git.kernel.org/stable/c/c0b6e2ae90613c2fea7eaf3faa20985c6c2a1953
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68141.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
