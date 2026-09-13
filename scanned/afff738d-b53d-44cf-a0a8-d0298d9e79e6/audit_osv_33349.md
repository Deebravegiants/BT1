# [H] net: use dst_dev_rcu() in sk_setup_caps()

## Summary
Severity: High
Advisory: CVE-2025-40170
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40170
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.12.64, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: use dst_dev_rcu() in sk_setup_caps()

Use RCU to protect accesses to dst->dev from sk_setup_caps()
and sk_dst_gso_max_size().

Also use dst_dev_rcu() in ip6_dst_mtu_maybe_forward(),
and ip_dst_mtu_maybe_forward().

ip4_dst_hoplimit() can use dst_dev_net_rcu().

## References
- https://git.kernel.org/stable/c/5d1be493d1110c9e720b4c51a6e587bb2fb4ac12
- https://git.kernel.org/stable/c/99a2ace61b211b0be861b07fbaa062fca4b58879
- https://git.kernel.org/stable/c/a805729c0091073d8f0415cfa96c7acd1bc17a48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40170.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40170
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
