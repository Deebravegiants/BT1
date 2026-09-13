# [H] drm/xe: reset mmio mappings with devm

## Summary
Severity: High
Advisory: CVE-2024-46705
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46705
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: reset mmio mappings with devm

Set our various mmio mappings to NULL. This should make it easier to
catch something rogue trying to mess with mmio after device removal. For
example, we might unmap everything and then start hitting some mmio
address which has already been unmamped by us and then remapped by
something else, causing all kinds of carnage.

## References
- https://git.kernel.org/stable/c/b1c9fbed3884d3883021d699c7cdf5253a65543a
- https://git.kernel.org/stable/c/c7117419784f612d59ee565145f722e8b5541fe6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46705.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46705
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
