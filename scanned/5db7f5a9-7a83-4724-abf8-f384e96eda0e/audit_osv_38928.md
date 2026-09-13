# [H] xsk: tighten UMEM headroom validation to account for tailroom and min frame

## Summary
Severity: High
Advisory: CVE-2026-43093
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43093
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: tighten UMEM headroom validation to account for tailroom and min frame

The current headroom validation in xdp_umem_reg() could leave us with
insufficient space dedicated to even receive minimum-sized ethernet
frame. Furthermore if multi-buffer would come to play then
skb_shared_info stored at the end of XSK frame would be corrupted.

HW typically works with 128-aligned sizes so let us provide this value
as bare minimum.

Multi-buffer setting is known later in the configuration process so
besides accounting for 128 bytes, let us also take care of tailroom space
upfront.

## References
- https://git.kernel.org/stable/c/0ec4d3f6e6934deb843b561ae048cd17218e5ad1
- https://git.kernel.org/stable/c/1a6051cd7e3e4c54ff3854a43b638b9292af5e67
- https://git.kernel.org/stable/c/5f123bc278bf4e3283d8606321bebbfd299f4384
- https://git.kernel.org/stable/c/6523bc1b40e69301f24c14338b762af4739d6d39
- https://git.kernel.org/stable/c/8769708add9eadeea8041a9761771bb715a87104
- https://git.kernel.org/stable/c/9ea6ba4f3195dcba6e8b3e7b2e748593b7cafb12
- https://git.kernel.org/stable/c/a03975beb9f6af0d8ac051e30b2abeabe618414f
- https://git.kernel.org/stable/c/a315e022a72d95ef5f1d4e58e903cb492b0ad931
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43093.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43093
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
