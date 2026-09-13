# [H] net: ethernet: ti: am65-cpsw: Fix NULL dereference on XDP_TX

## Summary
Severity: High
Advisory: CVE-2024-46799
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46799
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: ti: am65-cpsw: Fix NULL dereference on XDP_TX

If number of TX queues are set to 1 we get a NULL pointer
dereference during XDP_TX.

~# ethtool -L eth0 tx 1
~# ./xdp-trafficgen udp -A <ipv6-src> -a <ipv6-dst> eth0 -t 2
Transmitting on eth0 (ifindex 2)
[  241.135257] Unable to handle kernel NULL pointer dereference at virtual address 0000000000000030

Fix this by using actual TX queues instead of max TX queues
when picking the TX channel in am65_cpsw_ndo_xdp_xmit().

## References
- https://git.kernel.org/stable/c/0a50c35277f96481a5a6ed5faf347f282040c57d
- https://git.kernel.org/stable/c/2e7189d2b1de51fc2567676cd4f96c0fe0960b9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46799.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46799
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
