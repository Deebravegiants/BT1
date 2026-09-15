# [H] drm/xe/pt: prevent invalid cursor access for purged BOs

## Summary
Severity: High
Advisory: CVE-2026-72358
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72358
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/pt: prevent invalid cursor access for purged BOs

During a page table walk for binding, xe_pt_stage_bind() explicitly
skips initializing the xe_res_cursor for purged BOs, treating them
similarly to NULL VMAs by only setting the cursor size.

However, xe_pt_hugepte_possible() and xe_pt_scan_64K() did not check
if the BO was purged before attempting to walk the cursor using
xe_res_dma() and xe_res_next(). Because the cursor was left
uninitialized for purged BOs, this falls through and triggers
warnings like:

  WARNING: drivers/gpu/drm/xe/xe_res_cursor.h:274 at xe_res_next

Fix this by explicitly checking if the BO is purged in both
xe_pt_hugepte_possible() and xe_pt_scan_64K(), returning early just
as we do for NULL VMAs, avoiding the invalid cursor accesses entirely.

As a precaution, also zero-initialize the cursor in xe_pt_stage_bind()
to ensure we don't pass garbage data into the page table walkers
if we ever hit a similar edge case in the future.

(cherry picked from commit 4c7b9c6ece32440e5a435a92076d049450cd2d2e)

## References
- https://git.kernel.org/stable/c/2b6b3f98d0e93856bee38699b783c71cb0e9d67f
- https://git.kernel.org/stable/c/8a0fb57675be578c4db19deb4298ed08a70f0f1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72358.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72358
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
