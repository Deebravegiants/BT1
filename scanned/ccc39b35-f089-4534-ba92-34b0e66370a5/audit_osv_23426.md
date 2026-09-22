# [H] phylib: fix potential use-after-free

## Summary
Severity: High
Advisory: CVE-2022-48754
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48754
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <4.19.228, >=4.20.0 <5.4.176, >=5.5.0 <5.10.96, >=5.11.0 <5.15.19, >=5.16.0 <5.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

phylib: fix potential use-after-free

Commit bafbdd527d56 ("phylib: Add device reset GPIO support") added call
to phy_device_reset(phydev) after the put_device() call in phy_detach().

The comment before the put_device() call says that the phydev might go
away with put_device().

Fix potential use-after-free by calling phy_device_reset() before
put_device().

## References
- https://git.kernel.org/stable/c/67d271760b037ce0806d687ee6057edc8afd4205
- https://git.kernel.org/stable/c/aefaccd19379d6c4620269a162bfb88ff687f289
- https://git.kernel.org/stable/c/bd024e36f68174b1793906c39ca16cee0c9295c2
- https://git.kernel.org/stable/c/cb2fab10fc5e7a3aa1bb0a68a3abdcf3e37852af
- https://git.kernel.org/stable/c/cbda1b16687580d5beee38273f6241ae3725960c
- https://git.kernel.org/stable/c/f39027cbada43b33566c312e6be3db654ca3ad17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48754.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48754
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
