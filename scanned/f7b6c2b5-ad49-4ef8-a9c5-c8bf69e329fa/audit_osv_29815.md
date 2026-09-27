# [H] drm/amd/display: Check gpio_id before used as array index

## Summary
Severity: High
Advisory: CVE-2024-46818
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46818
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.109, >=6.2.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Check gpio_id before used as array index

[WHY & HOW]
GPIO_ID_UNKNOWN (-1) is not a valid value for array index and therefore
should be checked in advance.

This fixes 5 OVERRUN issues reported by Coverity.

## References
- https://git.kernel.org/stable/c/0184cca30cad74d88f5c875d4e26999e26325700
- https://git.kernel.org/stable/c/08e7755f754e3d2cef7d3a7da538d33526bd6f7c
- https://git.kernel.org/stable/c/276e3fd93e3beb5894eb1cc8480f9f417d51524d
- https://git.kernel.org/stable/c/2a5626eeb3b5eec7a36886f9556113dd93ec8ed6
- https://git.kernel.org/stable/c/3d4198ab612ad48f73383ad3bb5663e6f0cdf406
- https://git.kernel.org/stable/c/40c2e8bc117cab8bca8814735f28a8b121654a84
- https://git.kernel.org/stable/c/8520fdc8ecc38f240a8e9e7af89cca6739c3e790
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46818.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46818
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
