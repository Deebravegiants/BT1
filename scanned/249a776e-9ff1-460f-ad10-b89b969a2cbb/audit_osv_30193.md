# [M] net/sun3_82586: fix potential memory leak in sun3_82586_send_packet()

## Summary
Severity: Medium
Advisory: CVE-2024-50168
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50168
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sun3_82586: fix potential memory leak in sun3_82586_send_packet()

The sun3_82586_send_packet() returns NETDEV_TX_OK without freeing skb
in case of skb->len being too long, add dev_kfree_skb() to fix it.

## References
- https://git.kernel.org/stable/c/137010d26dc5cd47cd62fef77cbe952d31951b7a
- https://git.kernel.org/stable/c/1a17a4ac2d57102497fac53b53c666dba6a0c20d
- https://git.kernel.org/stable/c/2cb3f56e827abb22c4168ad0c1bbbf401bb2f3b8
- https://git.kernel.org/stable/c/6dc937a3086e344f965ca5c459f8f3eb6b68d890
- https://git.kernel.org/stable/c/84f2bac74000dbb7a177d9b98a17031ec8d07ec5
- https://git.kernel.org/stable/c/8d5b20fbc548650019afa96822b6a33ea4ec8aa5
- https://git.kernel.org/stable/c/9c6ce55e6f0bd1541f112833006b4052614c7d94
- https://git.kernel.org/stable/c/db755e55349045375c5c7036e8650afb3ff419d8
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50168.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50168
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
