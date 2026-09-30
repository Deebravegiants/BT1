# [C] ipv6: mcast: Fix potential UAF in MLD delayed work

## Summary
Severity: Critical
Advisory: CVE-2026-72322
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72322
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: mcast: Fix potential UAF in MLD delayed work

A race condition exists between device teardown and incoming MLD query
processing, leading to a Use-After-Free in the MLD delayed work.

During device destruction, the primary reference to inet6_dev is dropped,
which can drop its refcount to 0. The actual freeing of inet6_dev memory
is deferred via RCU.

Concurrently, the packet receive path runs under RCU read lock and obtains
the inet6_dev pointer. Because the memory is RCU-protected, CPU-0 can
safely dereference inet6_dev even if its refcount has hit 0.

However, if CPU-0 calls igmp6_event_query() and schedules delayed work, it
attempts to acquire a reference using in6_dev_hold(). This increments the
refcount from 0 to 1, triggering a "refcount_t: addition on 0" warning.
Since the inet6_dev memory is still scheduled to be freed after the RCU
grace period, the device is freed while the work is still scheduled.
When the work runs, it accesses the freed memory, causing a kernel panic.

Fix this by using refcount_inc_not_zero() (via a new helper
in6_dev_hold_safe()) to prevent acquiring a reference if the device is
already being destroyed. If the refcount is 0, we do not schedule the work.

## References
- https://git.kernel.org/stable/c/0401d6cf7877c9be36652385dfcbf7f891b8b590
- https://git.kernel.org/stable/c/0458ba1cda830ba4ccfcd9e19c0891438bcdbe4e
- https://git.kernel.org/stable/c/9815e834f5ff8b39e0ea9f0dbd532f4a3b8f0785
- https://git.kernel.org/stable/c/9b26518b6896a16b809b1e42986f4ebac7bccc1e
- https://git.kernel.org/stable/c/9ce741c22df4fd9546e30306317ac7df3607e48f
- https://git.kernel.org/stable/c/ebbebf6cee950d7f1c81990256c0eae9e62572ae
- https://git.kernel.org/stable/c/f03b0a45535d49bdab7e502efaacee205b2a7865
- https://git.kernel.org/stable/c/f12b63ef26a035c5a29b3ef56401e38199010d4a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72322.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72322
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
