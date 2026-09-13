# [H] netfilter: nft_fib: reject fib expression on the netdev egress hook

## Summary
Severity: High
Advisory: CVE-2026-72254
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72254
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_fib: reject fib expression on the netdev egress hook

A fib expression in a netdev egress base chain dereferences nft_in(pkt),
NULL on the transmit path, causing a NULL pointer dereference at eval.
nft_fib_validate() masks the hook with NF_INET_* values, but netdev hook
numbers are a separate enum that aliases them (NF_NETDEV_EGRESS ==
NF_INET_LOCAL_IN), so an egress chain passes validation and then faults.

Add nft_fib_netdev_validate() that limits each result/flag to the netdev
hook where the device it reads exists: the input-device cases (OIF,
OIFNAME, ADDRTYPE with F_IIF) to ingress, the output-device case (ADDRTYPE
with F_OIF) to egress, ADDRTYPE with no device flag to both. Also restrict
nft_fib_validate() to NFPROTO_IPV4/IPV6/INET so its NF_INET_* masks are
not applied to another family's hooks.

## References
- https://git.kernel.org/stable/c/4fee43759b489559a491f7c95f9bfa7a1d0c7a10
- https://git.kernel.org/stable/c/568931f26af4727a51e8521f72efbc78d3b82410
- https://git.kernel.org/stable/c/d01c913febead04a01a5f3a6374d1f45504dc523
- https://git.kernel.org/stable/c/d07955dd34ecae17d35d8c7d0a273a3fba653a8c
- https://git.kernel.org/stable/c/f68305267ebda7e839b5e8f77e8d77535a3d5a0f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72254.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72254
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
