# [H] netfilter: ipset: add the missing IP_SET_HASH_WITH_NET0 macro for ip_set_hash_netportnet.c

## Summary
Severity: High
Advisory: CVE-2023-53179
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53179
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.10.195, >=5.5.0 <5.15.132, >=5.11.0 <6.1.53, >=5.16.0 <6.4.16, >=6.2.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: add the missing IP_SET_HASH_WITH_NET0 macro for ip_set_hash_netportnet.c

The missing IP_SET_HASH_WITH_NET0 macro in ip_set_hash_netportnet can
lead to the use of wrong `CIDR_POS(c)` for calculating array offsets,
which can lead to integer underflow. As a result, it leads to slab
out-of-bound access.
This patch adds back the IP_SET_HASH_WITH_NET0 macro to
ip_set_hash_netportnet to address the issue.

## References
- https://git.kernel.org/stable/c/050d91c03b28ca479df13dfb02bcd2c60dd6a878
- https://git.kernel.org/stable/c/109e830585e89a03d554bf8ad0e668630d0a6260
- https://git.kernel.org/stable/c/7935b636dd693dfe4483cfef4a1e91366c8103fa
- https://git.kernel.org/stable/c/7ca0706c68adadf86a36b60dca090f5e9481e808
- https://git.kernel.org/stable/c/83091f8ac03f118086596f17c9a52d31d6ca94b3
- https://git.kernel.org/stable/c/a9e6142e5f8f6ac7d1bca45c1b2b13b084ea9e14
- https://git.kernel.org/stable/c/d59b6fc405549f7caf31f6aa5da1d6bef746b166
- https://git.kernel.org/stable/c/d95c8420efe684b964e3aa28108e9a354bcd7225
- https://git.kernel.org/stable/c/e632d09dffc68b9602d6893a99bfe3001d36cefc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53179.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53179
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
