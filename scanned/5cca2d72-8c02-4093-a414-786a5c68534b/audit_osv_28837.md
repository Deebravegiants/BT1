# [H] pinctrl: core: delete incorrect free in pinctrl_enable()

## Summary
Severity: High
Advisory: CVE-2024-36940
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36940
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: core: delete incorrect free in pinctrl_enable()

The "pctldev" struct is allocated in devm_pinctrl_register_and_init().
It's a devm_ managed pointer that is freed by devm_pinctrl_dev_release(),
so freeing it in pinctrl_enable() will lead to a double free.

The devm_pinctrl_dev_release() function frees the pindescs and destroys
the mutex as well.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/288bc4aa75f150d6f1ee82dd43c6da1b438b6068
- https://git.kernel.org/stable/c/41f88ef8ba387a12f4a2b8c400b6c9e8e54b2cca
- https://git.kernel.org/stable/c/5038a66dad0199de60e5671603ea6623eb9e5c79
- https://git.kernel.org/stable/c/558c8039fdf596a584a92c171cbf3298919c448c
- https://git.kernel.org/stable/c/735f4c6b6771eafe336404c157ca683ad72a040d
- https://git.kernel.org/stable/c/ac7d65795827dc0cf7662384ed27caf4066bd72e
- https://git.kernel.org/stable/c/cdaa171473d98962ae86f2a663d398fda2fbeefd
- https://git.kernel.org/stable/c/f9f1e321d53e4c5b666b66e5b43da29841fb55ba
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36940.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36940
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
