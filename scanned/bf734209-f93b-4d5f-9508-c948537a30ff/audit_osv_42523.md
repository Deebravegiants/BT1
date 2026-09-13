# [H] usb: musb: omap2430: Do not put borrowed of_node in probe

## Summary
Severity: High
Advisory: CVE-2026-68371
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68371
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.184, >=6.2.0 <6.12.101, >=6.7.0 <6.18.42, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: musb: omap2430: Do not put borrowed of_node in probe

omap2430_probe() stores pdev->dev.of_node in a local np variable. This is
a borrowed pointer and the probe function does not take a reference to
it.

The success and error paths nevertheless call of_node_put(np). This drops
a reference that is owned by the platform device, and can leave
pdev->dev.of_node with an unbalanced reference count.

Do not put the borrowed platform device node from omap2430_probe().
References taken for the child MUSB device are handled by the device core,
and the ctrl-module phandle reference is still released separately.

## References
- https://git.kernel.org/stable/c/0950ac52426b0ab32d3b8cf4afe1711668b19cb8
- https://git.kernel.org/stable/c/58d1c81c0b54a0b9aa6d6af077b09aa2f1bd2193
- https://git.kernel.org/stable/c/6c525c851e5912b9753622d796f2bc55c4913b04
- https://git.kernel.org/stable/c/c947360ae63eee1c9eacc030dd6f5a53f717addf
- https://git.kernel.org/stable/c/eed56f105a7f70cbcfceb4df6deb6870fc58214d
- https://git.kernel.org/stable/c/f0e68402d13cd9ffb289da50e65d4429d0002174
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68371.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68371
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
