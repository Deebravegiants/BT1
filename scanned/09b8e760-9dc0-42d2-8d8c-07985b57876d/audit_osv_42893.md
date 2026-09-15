# [H] can: bcm: add missing device refcount for CAN filter removal

## Summary
Severity: High
Advisory: CVE-2026-72113
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72113
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: add missing device refcount for CAN filter removal

sashiko-bot remarked a problem with a concurrent device unregistration
in isotp.c which also is present in the bcm.c code. A former fix for raw.c
commit c275a176e4b6 ("can: raw: add missing refcount for memory leak fix")
introduced a netdevice_tracker which solves the issue for bcm.c too.

bcm_release(), bcm_delete_rx_op() and bcm_notifier() relied on
dev_get_by_index(ifindex) to re-find the device for an rx_op before
unregistering its filter. If a concurrent NETDEV_UNREGISTER has already
unlisted the device from the ifindex table, that lookup fails and
can_rx_unregister() is silently skipped, leaving a stale CAN filter
pointing at the soon-to-be-freed bcm_op/socket.

Hold a netdev_hold()/netdev_put() tracked reference on op->rx_reg_dev
from the moment the rx filter is registered in bcm_rx_setup() until it
is unregistered in bcm_rx_unreg(), and use that reference directly in
bcm_release() and bcm_delete_rx_op() instead of re-looking the device
up by ifindex.

## References
- https://git.kernel.org/stable/c/04d23061bbf18d5d81022eb21e9d32e99d24468d
- https://git.kernel.org/stable/c/633bda66fbf309f5de5e1ad6defe8e6b1d77a20f
- https://git.kernel.org/stable/c/84aa4807816e405c1bf87114fc63e06d244281ef
- https://git.kernel.org/stable/c/b024c21c9066f6957b7d4a8f2037e4b000c5e041
- https://git.kernel.org/stable/c/bd5232663524e94cc5aad861dca11e3db8e2ab6f
- https://git.kernel.org/stable/c/d59948293ea34b6337ce2b5febab8510de70048c
- https://git.kernel.org/stable/c/dcaee869913c7210cd47ed0a8f27349d7bdcdb7b
- https://git.kernel.org/stable/c/ee8b36d0faca08f35b889b6e9aa850695e5b8ba9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72113
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
