# [M] fbdev: imsttfb: fix a resource leak in probe

## Summary
Severity: Medium
Advisory: CVE-2023-52838
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52838
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.299, >=4.20.0 <5.4.261, >=5.5.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.4.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: imsttfb: fix a resource leak in probe

I've re-written the error handling but the bug is that if init_imstt()
fails we need to call iounmap(par->cmap_regs).

## References
- https://git.kernel.org/stable/c/18d26f9baca7d0d309303e3074a2252b8310884a
- https://git.kernel.org/stable/c/382e1931e0c9cd58a5a8519cdc6cd9dc4d82b485
- https://git.kernel.org/stable/c/6c66d737b2726ac7784269ddf32a31634f8f269d
- https://git.kernel.org/stable/c/7bc7b82fb2191b0d50a80ee4e27030918767dd1d
- https://git.kernel.org/stable/c/8e4b510fe91782522b7ca0ca881b663b5d35e513
- https://git.kernel.org/stable/c/a4dfebec32ec6d420a5506dd56a7834c91be28e4
- https://git.kernel.org/stable/c/aba6ab57a910ad4b940c2024d15f2cdbf5b7f76b
- https://git.kernel.org/stable/c/b346a531159d08c564a312a9eaeea691704f3c00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52838.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52838
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
