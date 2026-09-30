# [C] ipv4: igmp: Fix potential UAF in igmp_gq_start_timer()

## Summary
Severity: Critical
Advisory: CVE-2026-72323
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72323
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.269, >=5.11.0 <5.15.220, >=5.16.0 <6.1.187, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: igmp: Fix potential UAF in igmp_gq_start_timer()

A race condition exists between device teardown (inetdev_destroy) and
incoming IGMP query processing (igmp_rcv), leading to a Use-After-Free
in the IGMP timer callback.

During device destruction, inetdev_destroy() drops the primary reference
to in_device, which can drop its refcount to 0. The actual freeing of
in_device memory is deferred via RCU (using call_rcu()).

Concurrently, igmp_rcv() runs under RCU read lock and obtains the
in_device pointer. Because the memory is RCU-protected, CPU-0 can safely
dereference in_device even if its refcount has hit 0.

However, if CPU-0 calls igmp_gq_start_timer() and re-arms the timer, it
attempts to acquire a reference using in_dev_hold(). This increments the
refcount from 0 to 1, triggering a "refcount_t: addition on 0" warning.
Since the in_device memory is still scheduled to be freed after the RCU
grace period (as the free callback does not check the refcount again),
the device is freed while the timer is still armed. When the timer
expires, it accesses the freed memory, causing a kernel panic.

Fix this by using refcount_inc_not_zero() (via a new helper
in_dev_hold_safe()) to prevent acquiring a reference if the device is
already being destroyed. If the refcount is 0, we do not arm the timer.

A similar issue in IPv6 MLD is fixed in a subsequent patch.

## References
- https://git.kernel.org/stable/c/165258303357e54b75fc19b341ae2a2b7c9e3910
- https://git.kernel.org/stable/c/40a1e998cb266ed4cb529a0bb4fee2b0ba732702
- https://git.kernel.org/stable/c/7265c747eec415ca3109a6a14a419f7ae433b780
- https://git.kernel.org/stable/c/74b301f7f197517016befb5f5dfab01f7bc64be5
- https://git.kernel.org/stable/c/75e984fe0cb9e7fbde0c8ee838c61ce8573d3ea3
- https://git.kernel.org/stable/c/7b19c0f81ed1fdaec6bc522569be367199a9edf3
- https://git.kernel.org/stable/c/8d4394ffa40508e0de72f464af351f6ca6a6cdc3
- https://git.kernel.org/stable/c/d107b4c4f8274763b7ea5ab05d45cef78e4b81ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72323.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72323
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
