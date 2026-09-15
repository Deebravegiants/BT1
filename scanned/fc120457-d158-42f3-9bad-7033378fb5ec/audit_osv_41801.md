# [H] usb: musb: omap2430: Fix use-after-free in omap2430_probe()

## Summary
Severity: High
Advisory: CVE-2026-63906
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63906
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.176, >=6.2.0 <6.12.93, >=6.7.0 <6.18.35, >=6.13.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: musb: omap2430: Fix use-after-free in omap2430_probe()

In omap2430_probe(), of_node_put(np) is called prematurely before the
last access to np, leading to a use-after-free if the node's reference
count drops to zero. Move the of_node_put() calls after the last use of
np in both the success and error paths.

## References
- https://git.kernel.org/stable/c/27e62532228dc42367bb43ebbcd7bf49d8db2b0d
- https://git.kernel.org/stable/c/632fd888fe33083927e29ef651ac1aba345edd9e
- https://git.kernel.org/stable/c/69f9f2b30af03d9b6e83f78fb0f734b6066d4678
- https://git.kernel.org/stable/c/b987f380620b38c84f054d5ff5c05861a7c2203b
- https://git.kernel.org/stable/c/d53e4c41331f57b9fd78cbf3e480c6ce20aea07b
- https://git.kernel.org/stable/c/e194ce048f5a6c549b3a23a8c568c6470f40f772
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63906.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63906
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
