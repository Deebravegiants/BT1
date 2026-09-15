# [H] net: openvswitch: Fix Use-After-Free in ovs_ct_exit

## Summary
Severity: High
Advisory: CVE-2024-27395
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-27395
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.158, >=5.16.0 <6.1.90, >=6.2.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: openvswitch: Fix Use-After-Free in ovs_ct_exit

Since kfree_rcu, which is called in the hlist_for_each_entry_rcu traversal
of ovs_ct_limit_exit, is not part of the RCU read critical section, it
is possible that the RCU grace period will pass during the traversal and
the key will be free.

To prevent this, it should be changed to hlist_for_each_entry_safe.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/2db9a8c0a01fa1c762c1e61a13c212c492752994
- https://git.kernel.org/stable/c/35880c3fa6f8fe281a19975d2992644588ca33d3
- https://git.kernel.org/stable/c/589523cf0b384164e445dd5db8d5b1bf97982424
- https://git.kernel.org/stable/c/5ea7b72d4fac2fdbc0425cd8f2ea33abe95235b2
- https://git.kernel.org/stable/c/9048616553c65e750d43846f225843ed745ec0d4
- https://git.kernel.org/stable/c/bca6fa2d9a9f560e6b89fd5190b05cc2f5d422c1
- https://git.kernel.org/stable/c/eaa5e164a2110d2fb9e16c8a29e4501882235137
- https://git.kernel.org/stable/c/edee0758747d7c219e29db9ed1d4eb33e8d32865
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27395.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27395
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
