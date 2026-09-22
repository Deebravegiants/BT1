# [M] wifi: rtlwifi: fix memory leaks and invalid access at probe error path

## Summary
Severity: Medium
Advisory: CVE-2024-58063
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58063
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtlwifi: fix memory leaks and invalid access at probe error path

Deinitialize at reverse order when probe fails.

When init_sw_vars fails, rtl_deinit_core should not be called, specially
now that it destroys the rtl_wq workqueue.

And call rtl_pci_deinit and deinit_sw_vars, otherwise, memory will be
leaked.

Remove pci_set_drvdata call as it will already be cleaned up by the core
driver code and could lead to memory leaks too. cf. commit 8d450935ae7f
("wireless: rtlwifi: remove unnecessary pci_set_drvdata()") and
commit 3d86b93064c7 ("rtlwifi: Fix PCI probe error path orphaned memory").

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/32acebca0a51f5e372536bfdc0d7d332ab749013
- https://git.kernel.org/stable/c/455e0f40b5352186a9095f2135d5c89255e7c39a
- https://git.kernel.org/stable/c/624cea89a0865a2bc3e00182a6b0f954a94328b4
- https://git.kernel.org/stable/c/6b76bab5c257463302c9e97f5d84d524457468eb
- https://git.kernel.org/stable/c/85b67b4c4a0f8a6fb20cf4ef7684ff2b0cf559df
- https://git.kernel.org/stable/c/b96371339fd9cac90f5ee4ac17ee5c4cbbdfa6f7
- https://git.kernel.org/stable/c/e7ceefbfd8d447abc8aca8ab993a942803522c06
- https://git.kernel.org/stable/c/ee0b0d7baa8a6d42c7988f6e50c8f164cdf3fa47
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58063.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58063
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
