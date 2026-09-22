# [C] net/smc: fix socket use-after-free during link group termination

## Summary
Severity: Critical
Advisory: CVE-2026-74493
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74493
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix socket use-after-free during link group termination

__smc_lgr_terminate() drops conns_lock after finding a connection in
lgr->conns_all, but before taking a reference on its socket. The connection
is embedded in the socket, and its registration reference protects it only
while the connection remains in the tree.

A concurrent close can unregister the connection and drop that reference,
freeing the socket before the termination worker reaches sock_hold().

The race is reachable when close overlaps link group termination.
Local stress testing reproduced the use-after-free and KASAN reported:

  BUG: KASAN: slab-use-after-free in __smc_lgr_terminate.part.0 [smc]
  Write of size 4 by task kworker/3:3
  Workqueue: events smc_lgr_terminate_work [smc]
  __smc_lgr_terminate.part.0 [smc]

The socket was allocated by smc_create(), freed through
slab_free_after_rcu_debug(), and was followed by:

  refcount_t: addition on 0; use-after-free.
  __smc_lgr_terminate.part.0 [smc]

Take the socket reference while conns_lock still protects the tree entry.
The unregister path then cannot drop the last reference until termination
has finished using the socket.

## References
- https://git.kernel.org/stable/c/281c103a8eaed59001ce952f231df1b07674215a
- https://git.kernel.org/stable/c/5a42f162b857019a4c10ff687dc3bcdf51831865
- https://git.kernel.org/stable/c/9fb17c95b8f0683570fca1fb2792264147af937a
- https://git.kernel.org/stable/c/bea8dc14de2d56aca749d368563e6888217710a5
- https://git.kernel.org/stable/c/f0541a775d04c88e90ba448e35ce0d743512822a
- https://git.kernel.org/stable/c/f621d6ebeebb6374342571e4ddf45fdbc420f6cd
- https://git.kernel.org/stable/c/f807a63d0d95680c34f677700da9148a07d7c78f
- https://git.kernel.org/stable/c/ff44f2df57fb5560bdc75eb977867643e764a262
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74493.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74493
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
