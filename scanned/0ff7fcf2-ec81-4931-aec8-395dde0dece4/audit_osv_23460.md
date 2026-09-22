# [C] staging: gdm724x: fix use after free in gdm_lte_rx()

## Summary
Severity: Critical
Advisory: CVE-2022-48851
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48851
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.9.307, >=4.10.0 <4.14.272, >=4.15.0 <4.19.235, >=4.20.0 <5.4.185, >=5.5.0 <5.10.106, >=5.11.0 <5.15.29, >=5.16.0 <5.16.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: gdm724x: fix use after free in gdm_lte_rx()

The netif_rx_ni() function frees the skb so we can't dereference it to
save the skb->len.

## References
- https://git.kernel.org/stable/c/1fb9dd3787495b4deb0efe66c58306b65691a48f
- https://git.kernel.org/stable/c/403e3afe241b62401de1f8629c9c6b9b3d69dbff
- https://git.kernel.org/stable/c/48ecdf3e29a6e514e8196691589c7dfc6c4ac169
- https://git.kernel.org/stable/c/6d9700b445098dbbce0caff4b8cfca214cf1e757
- https://git.kernel.org/stable/c/6dc7b87c62423bfa68139fe95e85028aab584c9a
- https://git.kernel.org/stable/c/83a9c886c2b5a0d28c0b37e1736b47f38d61332a
- https://git.kernel.org/stable/c/d39dc79513e99147b4c158a8a9e46743e23944f5
- https://git.kernel.org/stable/c/fc7f750dc9d102c1ed7bbe4591f991e770c99033
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48851.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48851
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
