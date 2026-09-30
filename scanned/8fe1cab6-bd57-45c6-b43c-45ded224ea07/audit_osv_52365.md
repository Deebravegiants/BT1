# [H] CVE-2021-47372

## Summary
Severity: High
Advisory: CVE-2021-47372
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47372
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: macb: fix use after free on rmmod

plat_dev->dev->platform_data is released by platform_device_unregister(),
use of pclk and hclk is a use-after-free. Since device unregister won't
need a clk device we adjust the function call sequence to fix this issue.

[   31.261225] BUG: KASAN: use-after-free in macb_remove+0x77/0xc6 [macb_pci]
[   31.275563] Freed by task 306:
[   30.276782]  platform_device_release+0x25/0x80

## References
- https://git.kernel.org/stable/c/1da750d1e2140ef43d64d17f301ff6f41b45541e
- https://git.kernel.org/stable/c/46670fb832ee80943715df618632ca13c2e96f2b
- https://git.kernel.org/stable/c/4ad6f2d23b0f6ac0d3e5f3102a4256d1c86c90f5
- https://git.kernel.org/stable/c/7721221e87d25c9840d9ca6b986dbdc410d5ce2b
- https://git.kernel.org/stable/c/a7d521cc726f30b8e679a6f36d04b18a8ab3c536
- https://git.kernel.org/stable/c/d82d5303c4c539db86588ffb5dc5b26c3f1513e8
