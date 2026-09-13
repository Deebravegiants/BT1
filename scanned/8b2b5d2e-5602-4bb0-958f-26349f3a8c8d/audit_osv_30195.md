# [H] net: bcmasp: fix potential memory leak in bcmasp_xmit()

## Summary
Severity: High
Advisory: CVE-2024-50170
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50170
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bcmasp: fix potential memory leak in bcmasp_xmit()

The bcmasp_xmit() returns NETDEV_TX_OK without freeing skb
in case of mapping fails, add dev_kfree_skb() to fix it.

## References
- https://git.kernel.org/stable/c/7218de0778aefbbbcfe474a55f88bbf6f244627d
- https://git.kernel.org/stable/c/f689f20d3e09f2d4d0a2c575a9859115a33e68bd
- https://git.kernel.org/stable/c/fed07d3eb8a8d9fcc0e455175a89bc6445d6faed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50170.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50170
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
