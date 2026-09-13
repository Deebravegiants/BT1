# [M] CVE-2019-12819

## Summary
Severity: Medium
Advisory: CVE-2019-12819
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-14
Source: https://osv.dev/vulnerability/CVE-2019-12819
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0. The function __mdiobus_register() in drivers/net/phy/mdio_bus.c calls put_device(), which will trigger a fixed_mdio_bus_init use-after-free. This will cause a denial of service.

## References
- https://usn.ubuntu.com/4094-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00048.html
- http://packetstormsecurity.com/files/154245/Kernel-Live-Patch-Security-Notice-LSN-0054-1.html
- https://usn.ubuntu.com/4118-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00040.html
- http://www.securityfocus.com/bid/108768
- https://security.netapp.com/advisory/ntap-20190710-0002/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6ff7b060535e87c2ae14dd8548512abfdda528fb
- https://github.com/torvalds/linux/commit/6ff7b060535e87c2ae14dd8548512abfdda528fb
