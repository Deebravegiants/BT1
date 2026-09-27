# [H] drm/amd/display: Check link_index before accessing dc->links[]

## Summary
Severity: High
Advisory: CVE-2024-46813
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46813
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.6.87, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Check link_index before accessing dc->links[]

[WHY & HOW]
dc->links[] has max size of MAX_LINKS and NULL is return when trying to
access with out-of-bound index.

This fixes 3 OVERRUN and 1 RESOURCE_LEAK issues reported by Coverity.

## References
- https://git.kernel.org/stable/c/032c5407a608ac3b2a98bf4fbda27d12c20c5887
- https://git.kernel.org/stable/c/8aa2864044b9d13e95fe224f32e808afbf79ecdf
- https://git.kernel.org/stable/c/ac04759b4a002969cf0f1384f1b8bb2001cfa782
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46813.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46813
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
