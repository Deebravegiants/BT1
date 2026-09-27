# [H] net: davicom: fix UAF in dm9000_drv_remove

## Summary
Severity: High
Advisory: CVE-2025-21715
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21715
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.12.0 <6.1.129, >=5.16.0 <6.6.76, >=6.2.0 <6.12.13, >=6.7.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: davicom: fix UAF in dm9000_drv_remove

dm is netdev private data and it cannot be
used after free_netdev() call. Using dm after free_netdev()
can cause UAF bug. Fix it by moving free_netdev() at the end of the
function.

This is similar to the issue fixed in commit
ad297cd2db89 ("net: qcom/emac: fix UAF in emac_remove").

This bug is detected by our static analysis tool.

## References
- https://git.kernel.org/stable/c/19e65c45a1507a1a2926649d2db3583ed9d55fd9
- https://git.kernel.org/stable/c/2013c95df6752d9c88221d0f0f37b6f197969390
- https://git.kernel.org/stable/c/5a54367a7c2378c65aaa4d3cfd952f26adef7aa7
- https://git.kernel.org/stable/c/7d7d201eb3b766abe590ac0dda7a508b7db3e357
- https://git.kernel.org/stable/c/a53cb72043443ac787ec0b5fa17bb3f8ff3d462b
- https://git.kernel.org/stable/c/c411f9a5fdc9158e8f7c57eac961d3df3eb4d8ca
- https://git.kernel.org/stable/c/c94ab07edc2843e2f3d46dbd82e5c681503aaadf
- https://git.kernel.org/stable/c/db79e982c5f9e39ab710cbce55b05f2f5e6f1ca9
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21715.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21715
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
