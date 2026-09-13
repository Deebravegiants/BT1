# [H] mctp: perform route lookups under a RCU read-side lock

## Summary
Severity: High
Advisory: CVE-2023-52483
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52483
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.137, >=5.16.0 <6.1.59, >=6.2.0 <6.5.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mctp: perform route lookups under a RCU read-side lock

Our current route lookups (mctp_route_lookup and mctp_route_lookup_null)
traverse the net's route list without the RCU read lock held. This means
the route lookup is subject to preemption, resulting in an potential
grace period expiry, and so an eventual kfree() while we still have the
route pointer.

Add the proper read-side critical section locks around the route
lookups, preventing premption and a possible parallel kfree.

The remaining net->mctp.routes accesses are already under a
rcu_read_lock, or protected by the RTNL for updates.

Based on an analysis from Sili Luo <rootlab@huawei.com>, where
introducing a delay in the route lookup could cause a UAF on
simultaneous sendmsg() and route deletion.

## References
- https://git.kernel.org/stable/c/1db0724a01b558feb1ecae551782add1951a114a
- https://git.kernel.org/stable/c/2405f64a95a7a094eb24cba9bcfaffd1ea264de4
- https://git.kernel.org/stable/c/5093bbfc10ab6636b32728e35813cbd79feb063c
- https://git.kernel.org/stable/c/6c52b12159049046483fdb0c411a0a1869c41a67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52483.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52483
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
