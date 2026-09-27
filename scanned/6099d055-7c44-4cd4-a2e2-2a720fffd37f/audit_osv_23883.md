# [M] net: sfp: fix memory leak in sfp_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49619
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49619
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.14.289, >=4.15.0 <4.19.253, >=4.20.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sfp: fix memory leak in sfp_probe()

sfp_probe() allocates a memory chunk from sfp with sfp_alloc(). When
devm_add_action() fails, sfp is not freed, which leads to a memory leak.

We should use devm_add_action_or_reset() instead of devm_add_action().

## References
- https://git.kernel.org/stable/c/0a18d802d65cf662644fd1d369c86d84a5630652
- https://git.kernel.org/stable/c/1545bc727625ea6e8decd717e5d1e8cc704ccf8f
- https://git.kernel.org/stable/c/204543581a2f26bb3b997a304c0bd06926ba7f15
- https://git.kernel.org/stable/c/67dc32542a1fb7790d0853cf4a5cf859ac6a2002
- https://git.kernel.org/stable/c/9ec5a97f327a89031fce6cfc3e95543c53936638
- https://git.kernel.org/stable/c/ede990cfc42775bd0141e21f37ee365dcaeeb50f
- https://git.kernel.org/stable/c/f22ddc8a5278d7fb6369a0aeb0d8775a0aefaaee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49619.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49619
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
