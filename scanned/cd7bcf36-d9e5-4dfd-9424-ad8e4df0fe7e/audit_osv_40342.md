# [H] netfilter: nfnetlink_osf: fix potential NULL dereference in ttl check

## Summary
Severity: High
Advisory: CVE-2026-52998
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52998
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nfnetlink_osf: fix potential NULL dereference in ttl check

The nf_osf_ttl() function accessed skb->dev to perform a local interface
address lookup without verifying that the device pointer was valid.

Additionally, the implementation utilized an in_dev_for_each_ifa_rcu
loop to match the packet source address against local interface
addresses. It assumed that packets from the same subnet should not see a
decrement on the initial TTL. A packet might appear it is from the same
subnet but it actually isn't especially in modern environments with
containers and virtual switching.

Remove the device dereference and interface loop. Replace the logic with
a switch statement that evaluates the TTL according to the ttl_check.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/5d05de2f0928d81309a815ecc76d1a3ad72cbc16
- https://git.kernel.org/stable/c/711987ba281fd806322a7cd244e98e2a81903114
- https://git.kernel.org/stable/c/79b90a96688e521771fa6ed3dc7864b76b8df293
- https://git.kernel.org/stable/c/83fc5dd63455a779ea2dd0f7ffee3c920919d80b
- https://git.kernel.org/stable/c/95be653a76793856ff8b2d8bd82c2943c23f5ca8
- https://git.kernel.org/stable/c/c996a90f3071cf43683e5423da31aadbe002b8b4
- https://git.kernel.org/stable/c/edc806f9122961f0d3819f7c69c14cccde31f277
- https://git.kernel.org/stable/c/f4de0777e4554a7de19c920accde6319dd530782
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52998.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52998
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
