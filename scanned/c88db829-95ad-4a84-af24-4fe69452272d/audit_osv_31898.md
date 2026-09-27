# [C] netmem: prevent TX of unreadable skbs

## Summary
Severity: Critical
Advisory: CVE-2025-21954
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21954
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netmem: prevent TX of unreadable skbs

Currently on stable trees we have support for netmem/devmem RX but not
TX. It is not safe to forward/redirect an RX unreadable netmem packet
into the device's TX path, as the device may call dma-mapping APIs on
dma addrs that should not be passed to it.

Fix this by preventing the xmit of unreadable skbs.

Tested by configuring tc redirect:

sudo tc qdisc add dev eth1 ingress
sudo tc filter add dev eth1 ingress protocol ip prio 1 flower ip_proto \
	tcp src_ip 192.168.1.12 action mirred egress redirect dev eth1

Before, I see unreadable skbs in the driver's TX path passed to dma
mapping APIs.

After, I don't see unreadable skbs in the driver's TX path passed to dma
mapping APIs.

## References
- https://git.kernel.org/stable/c/1c17c8ced25c5fbe424c7ad7ea11d33014a986b1
- https://git.kernel.org/stable/c/454825019d2f0c59e5174ece9e713f45ad80beff
- https://git.kernel.org/stable/c/f3600c867c99a2cc8038680ecf211089c50e7971
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21954.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21954
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
