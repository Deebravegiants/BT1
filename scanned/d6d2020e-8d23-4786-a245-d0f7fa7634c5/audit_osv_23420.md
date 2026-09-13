# [H] net: amd-xgbe: Fix skb data length underflow

## Summary
Severity: High
Advisory: CVE-2022-48743
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48743
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.300, >=4.10.0 <4.14.265, >=4.11.0 <4.19.228, >=4.15.0 <5.4.177, >=4.20.0 <5.10.97, >=5.5.0 <5.15.20, >=5.11.0 <5.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: amd-xgbe: Fix skb data length underflow

There will be BUG_ON() triggered in include/linux/skbuff.h leading to
intermittent kernel panic, when the skb length underflow is detected.

Fix this by dropping the packet if such length underflows are seen
because of inconsistencies in the hardware descriptors.

## References
- https://git.kernel.org/stable/c/34aeb4da20f93ac80a6291a2dbe7b9c6460e9b26
- https://git.kernel.org/stable/c/4d3fcfe8464838b3920bc2b939d888e0b792934e
- https://git.kernel.org/stable/c/5aac9108a180fc06e28d4e7fb00247ce603b72ee
- https://git.kernel.org/stable/c/617f9934bb37993b9813832516f318ba874bcb7d
- https://git.kernel.org/stable/c/9892742f035f7aa7dcd2bb0750effa486db89576
- https://git.kernel.org/stable/c/9924c80bd484340191e586110ca22bff23a49f2e
- https://git.kernel.org/stable/c/db6fd92316a254be2097556f01bccecf560e53ce
- https://git.kernel.org/stable/c/e8f73f620fee5f52653ed2da360121e4446575c5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48743.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48743
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
