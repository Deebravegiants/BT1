# [H] net: macsec: Fix offload support for NETDEV_UNREGISTER event

## Summary
Severity: High
Advisory: CVE-2022-48720
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48720
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.99, >=5.11.0 <5.15.22, >=5.16.0 <5.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: macsec: Fix offload support for NETDEV_UNREGISTER event

Current macsec netdev notify handler handles NETDEV_UNREGISTER event by
releasing relevant SW resources only, this causes resources leak in case
of macsec HW offload, as the underlay driver was not notified to clean
it's macsec offload resources.

Fix by calling the underlay driver to clean it's relevant resources
by moving offload handling from macsec_dellink() to macsec_common_dellink()
when handling NETDEV_UNREGISTER event.

## References
- https://git.kernel.org/stable/c/2e7f5b6ee1a7a2c628253a95b0a95b582901ef1b
- https://git.kernel.org/stable/c/8299be160aad8548071d080518712dec0df92bd5
- https://git.kernel.org/stable/c/9cef24c8b76c1f6effe499d2f131807c90f7ce9a
- https://git.kernel.org/stable/c/e7a0b3a0806dae3cc81931f0e83055ca2ac6f455
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48720.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48720
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
