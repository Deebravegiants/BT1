# [M] drm/radeon: Fix integer overflow in radeon_cs_parser_init

## Summary
Severity: Medium
Advisory: CVE-2023-53309
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53309
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <4.14.324, >=4.15.0 <4.19.293, >=4.20.0 <5.4.255, >=5.5.0 <5.10.192, >=5.11.0 <5.15.123, >=5.16.0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/radeon: Fix integer overflow in radeon_cs_parser_init

The type of size is unsigned, if size is 0x40000000, there will be an
integer overflow, size will be zero after size *= sizeof(uint32_t),
will cause uninitialized memory to be referenced later

## References
- https://git.kernel.org/stable/c/25e634d7f44eb13113139040e5366bebe48c882f
- https://git.kernel.org/stable/c/2e1be420b86980c25a75325e90dfc3fc73126f61
- https://git.kernel.org/stable/c/b8fab6aebdf2115ec2d7bd2f3498d5b911ff351e
- https://git.kernel.org/stable/c/c0d7dbc6b7a61a56028118c00af2c8319d44a682
- https://git.kernel.org/stable/c/cfa9148bafb2d3292b65de1bac79dcca65be2643
- https://git.kernel.org/stable/c/d05ba46134d07e889de7d23cf8503574a22ede09
- https://git.kernel.org/stable/c/e6825b30d37fe89ceb87f926d33d4fad321a331e
- https://git.kernel.org/stable/c/f828b681d0cd566f86351c0b913e6cb6ed8c7b9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53309.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53309
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
