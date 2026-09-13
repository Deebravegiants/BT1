# [M] net: systemport: fix potential memory leak in bcm_sysport_xmit()

## Summary
Severity: Medium
Advisory: CVE-2024-50171
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50171
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: systemport: fix potential memory leak in bcm_sysport_xmit()

The bcm_sysport_xmit() returns NETDEV_TX_OK without freeing skb
in case of dma_map_single() fails, add dev_kfree_skb() to fix it.

## References
- https://git.kernel.org/stable/c/31701ef0c4547973991ff63596c927f841dfd133
- https://git.kernel.org/stable/c/4b70478b984af3c9d0279c121df5ff94e2533dbd
- https://git.kernel.org/stable/c/533d2f30aef272dade17870a509521c3afc38a03
- https://git.kernel.org/stable/c/5febfc545389805ce83d37f9f4317055b26dd7d7
- https://git.kernel.org/stable/c/7d5030a819c3589cf9948b1eee397b626ec590f5
- https://git.kernel.org/stable/c/8e81ce7d0166a2249deb6d5e42f28a8b8c9ea72f
- https://git.kernel.org/stable/c/b6321146773dcbbc372a54dbada67e0b50e0a25c
- https://git.kernel.org/stable/c/c401ed1c709948e57945485088413e1bb5e94bd1
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50171.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50171
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
