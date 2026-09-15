# [H] gpu: host1x: Fix use-after-free in host1x_bo_clear_cached_mappings

## Summary
Severity: High
Advisory: CVE-2026-68427
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68427
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.178 <6.1.183, >=6.6.145 <6.6.148, >=6.12.97 <6.12.101, >=6.18.40 <6.18.42, >=7.1.5 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpu: host1x: Fix use-after-free in host1x_bo_clear_cached_mappings

__host1x_bo_unpin() drops the last reference to the mapping and frees
it, so we can't dereference mapping afterwards. The cache itself
outlives the mapping, so use the cache local variable instead.

## References
- https://git.kernel.org/stable/c/266cddf7bd0f6c79b6c0633aef742a22bf70265b
- https://git.kernel.org/stable/c/5b7e5f84d3d4cea10c3764d2da274810a7934228
- https://git.kernel.org/stable/c/5f4de3c717d34a24d555af581947742980778c02
- https://git.kernel.org/stable/c/86a9bd8c8f422d5f3079da31e151868902fcc702
- https://git.kernel.org/stable/c/abeff53233b984571b87582bb588b4b38ef4ea50
- https://git.kernel.org/stable/c/b773faa32b0a98c3eb2b50d96de631681e5d1157
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68427.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68427
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
