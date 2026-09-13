# [H] usbnet: Run unregister_netdev() before unbind() again

## Summary
Severity: High
Advisory: CVE-2022-49501
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49501
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

usbnet: Run unregister_netdev() before unbind() again

Commit 2c9d6c2b871d ("usbnet: run unbind() before unregister_netdev()")
sought to fix a use-after-free on disconnect of USB Ethernet adapters.

It turns out that a different fix is necessary to address the issue:
https://lore.kernel.org/netdev/18b3541e5372bc9b9fc733d422f4e698c089077c.1650177997.git.lukas@wunner.de/

So the commit was not necessary.

The commit made binding and unbinding of USB Ethernet asymmetrical:
Before, usbnet_probe() first invoked the ->bind() callback and then
register_netdev().  usbnet_disconnect() mirrored that by first invoking
unregister_netdev() and then ->unbind().

Since the commit, the order in usbnet_disconnect() is reversed and no
longer mirrors usbnet_probe().

One consequence is that a PHY disconnected (and stopped) in ->unbind()
is afterwards stopped once more by unregister_netdev() as it closes the
netdev before unregistering.  That necessitates a contortion in ->stop()
because the PHY may only be stopped if it hasn't already been
disconnected.

Reverting the commit allows making the call to phy_stop() unconditional
in ->stop().

## References
- https://git.kernel.org/stable/c/6d5deb242874d924beccf7eb3cef04c1c3b0da79
- https://git.kernel.org/stable/c/969a1b3ea3cb7d58a16fe12fd1b04bfc0ea40509
- https://git.kernel.org/stable/c/d1408f6b4dd78fb1b9e26bcf64477984e5f85409
- https://git.kernel.org/stable/c/fbda837107f9bd4ec658d2aa88c6856dba606f06
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49501.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49501
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
