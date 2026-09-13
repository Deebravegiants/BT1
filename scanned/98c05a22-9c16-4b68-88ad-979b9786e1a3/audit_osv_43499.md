# [H] cxl/region: Fix out-of-bounds access in cxl_cancel_auto_attach()

## Summary
Severity: High
Advisory: CVE-2026-74275
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74275
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl/region: Fix out-of-bounds access in cxl_cancel_auto_attach()

In cxl_cancel_auto_attach(), it assumes cxled->pos is a valid index for
accessing p->targets[]. However, cxled->pos can be set to negative errno
in cxl_region_sort_targets() if cxl_calc_interleave_pos() fails. This
causes the driver to use a negative index to access p->targets[],
resulting in out-of-bounds access.

Fix it by walking p->targets[] instead of using cxled->pos directly.

## References
- https://git.kernel.org/stable/c/44b2397eb67b7f728640989a22d062e41f94ab64
- https://git.kernel.org/stable/c/cbda6a2c2bec2a5fb30a2ce85baeab15b5fc7db3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74275.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74275
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
