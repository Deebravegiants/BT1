# [C] ipv4: start using dst_dev_rcu()

## Summary
Severity: Critical
Advisory: CVE-2025-40074
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40074
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.12.106, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: start using dst_dev_rcu()

Change icmpv4_xrlim_allow(), ip_defrag() to prevent possible UAF.

Change ipmr_prepare_xmit(), ipmr_queue_fwd_xmit(), ip_mr_output(),
ipv4_neigh_lookup() to use lockdep enabled dst_dev_rcu().

## References
- https://git.kernel.org/stable/c/684efb2c86c887685f9aa65e1a21b3df6c1f822d
- https://git.kernel.org/stable/c/6ad8de3cefdb6ffa6708b21c567df0dbf82c43a8
- https://git.kernel.org/stable/c/923e0734c386984d45de508528a7a7ad91d791cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40074.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40074
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
