# [H] usb: musb: sunxi: Fix accessing an released usb phy

## Summary
Severity: High
Advisory: CVE-2024-50269
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50269
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: musb: sunxi: Fix accessing an released usb phy

Commit 6ed05c68cbca ("usb: musb: sunxi: Explicitly release USB PHY on
exit") will cause that usb phy @glue->xceiv is accessed after released.

1) register platform driver @sunxi_musb_driver
// get the usb phy @glue->xceiv
sunxi_musb_probe() -> devm_usb_get_phy().

2) register and unregister platform driver @musb_driver
musb_probe() -> sunxi_musb_init()
use the phy here
//the phy is released here
musb_remove() -> sunxi_musb_exit() -> devm_usb_put_phy()

3) register @musb_driver again
musb_probe() -> sunxi_musb_init()
use the phy here but the phy has been released at 2).
...

Fixed by reverting the commit, namely, removing devm_usb_put_phy()
from sunxi_musb_exit().

## References
- https://git.kernel.org/stable/c/498dbd9aea205db9da674994b74c7bf8e18448bd
- https://git.kernel.org/stable/c/4aa77d5ea9944468e16c3eed15e858fd5de44de1
- https://git.kernel.org/stable/c/63559ba8077cbadae1c92a65b73ea522bf377dd9
- https://git.kernel.org/stable/c/6e2848d1c8c0139161e69ac0a94133e90e9988e8
- https://git.kernel.org/stable/c/721ddad945596220c123eb6f7126729fe277ee4f
- https://git.kernel.org/stable/c/8a30da5aa9609663b3e05bcc91a916537f66a4cd
- https://git.kernel.org/stable/c/b08baa75b989cf779cbfa0969681f8ba2dc46569
- https://git.kernel.org/stable/c/ccd811c304d2ee56189bfbc49302cb3c44361893
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50269.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50269
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
