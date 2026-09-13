# [M] CVE-2021-4135

## Summary
Severity: Medium
Advisory: CVE-2021-4135
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-07-14
Source: https://osv.dev/vulnerability/CVE-2021-4135
Type: osv

## Details
A memory leak vulnerability was found in the Linux kernel's eBPF for the Simulated networking device driver in the way user uses BPF for the device such that function nsim_map_alloc_elem being called. A local user could use this flaw to get unauthorized access to some data.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=481221775d53
