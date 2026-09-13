# [H] ravb: Fix use-after-free issue in ravb_tx_timeout_work()

## Summary
Severity: High
Advisory: CVE-2023-52509
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52509
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.4.259, >=5.5.0 <5.10.199, >=5.11.0 <5.15.136, >=5.16.0 <6.1.59, >=6.2.0 <6.5.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ravb: Fix use-after-free issue in ravb_tx_timeout_work()

The ravb_stop() should call cancel_work_sync(). Otherwise,
ravb_tx_timeout_work() is possible to use the freed priv after
ravb_remove() was called like below:

CPU0			CPU1
			ravb_tx_timeout()
ravb_remove()
unregister_netdev()
free_netdev(ndev)
// free priv
			ravb_tx_timeout_work()
			// use priv

unregister_netdev() will call .ndo_stop() so that ravb_stop() is
called. And, after phy_stop() is called, netif_carrier_off()
is also called. So that .ndo_tx_timeout() will not be called
after phy_stop().

## References
- https://git.kernel.org/stable/c/105abd68ad8f781985113aee2e92e0702b133705
- https://git.kernel.org/stable/c/3971442870713de527684398416970cf025b4f89
- https://git.kernel.org/stable/c/616761cf9df9af838c0a1a1232a69322a9eb67e6
- https://git.kernel.org/stable/c/65d34cfd4e347054eb4193bc95d9da7eaa72dee5
- https://git.kernel.org/stable/c/6f6fa8061f756aedb93af12a8a5d3cf659127965
- https://git.kernel.org/stable/c/db9aafa19547833240f58c2998aed7baf414dc82
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52509.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52509
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
