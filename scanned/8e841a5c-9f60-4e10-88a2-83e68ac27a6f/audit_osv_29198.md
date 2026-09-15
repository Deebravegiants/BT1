# [C] gve: Clear napi->skb before dev_kfree_skb_any()

## Summary
Severity: Critical
Advisory: CVE-2024-40937
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40937
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

gve: Clear napi->skb before dev_kfree_skb_any()

gve_rx_free_skb incorrectly leaves napi->skb referencing an skb after it
is freed with dev_kfree_skb_any(). This can result in a subsequent call
to napi_get_frags returning a dangling pointer.

Fix this by clearing napi->skb before the skb is freed.

## References
- https://git.kernel.org/stable/c/2ce5341c36993b776012601921d7688693f8c037
- https://git.kernel.org/stable/c/6f4d93b78ade0a4c2cafd587f7b429ce95abb02e
- https://git.kernel.org/stable/c/75afd8724739ee5ed8165acde5f6ac3988b485cc
- https://git.kernel.org/stable/c/a68184d5b420ea4fc7e6b7ceb52bbc66f90d3c50
- https://git.kernel.org/stable/c/d221284991118c0ab16480b53baecd857c0bc442
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40937.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40937
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
