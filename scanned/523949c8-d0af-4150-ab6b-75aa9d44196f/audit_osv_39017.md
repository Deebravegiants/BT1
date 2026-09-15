# [H] drm/i915: Fix potential overflow of shmem scatterlist length

## Summary
Severity: High
Advisory: CVE-2026-43368
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43368
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: Fix potential overflow of shmem scatterlist length

When a scatterlists table of a GEM shmem object of size 4 GB or more is
populated with pages allocated from a folio, unsigned int .length
attribute of a scatterlist may get overflowed if total byte length of
pages allocated to that single scatterlist happens to reach or cross the
4GB limit.  As a consequence, users of the object may suffer from hitting
unexpected, premature end of the object's backing pages.

[278.780187] ------------[ cut here ]------------
[278.780377] WARNING: CPU: 1 PID: 2326 at drivers/gpu/drm/i915/i915_mm.c:55 remap_sg+0x199/0x1d0 [i915]
...
[278.780654] CPU: 1 UID: 0 PID: 2326 Comm: gem_mmap_offset Tainted: G S   U              6.17.0-rc1-CI_DRM_16981-ged823aaa0607+ #1 PREEMPT(voluntary)
[278.780656] Tainted: [S]=CPU_OUT_OF_SPEC, [U]=USER
[278.780658] Hardware name: Intel Corporation Meteor Lake Client Platform/MTL-P LP5x T3 RVP, BIOS MTLPFWI1.R00.3471.D91.2401310918 01/31/2024
[278.780659] RIP: 0010:remap_sg+0x199/0x1d0 [i915]
...
[278.780786] Call Trace:
[278.780787]  <TASK>
[278.780788]  ? __apply_to_page_range+0x3e6/0x910
[278.780795]  ? __pfx_remap_sg+0x10/0x10 [i915]
[278.780906]  apply_to_page_range+0x14/0x30
[278.780908]  remap_io_sg+0x14d/0x260 [i915]
[278.781013]  vm_fault_cpu+0xd2/0x330 [i915]
[278.781137]  __do_fault+0x3a/0x1b0
[278.781140]  do_fault+0x322/0x640
[278.781143]  __handle_mm_fault+0x938/0xfd0
[278.781150]  handle_mm_fault+0x12c/0x300
[278.781152]  ? lock_mm_and_find_vma+0x4b/0x760
[278.781155]  do_user_addr_fault+0x2d6/0x8e0
[278.781160]  exc_page_fault+0x96/0x2c0
[278.781165]  asm_exc_page_fault+0x27/0x30
...

That issue was apprehended by the author of a change that introduced it,
and potential risk even annotated with a comment, but then never addressed.

When adding folio pages to a scatterlist table, take care of byte length
of any single scatterlist not exceeding max_segment.

(cherry picked from commit 06249b4e691a75694c014a61708c007fb5755f60)

## References
- https://git.kernel.org/stable/c/029ae067431ab9d0fca479bdabe780fa436706ea
- https://git.kernel.org/stable/c/1c956f0fccc26fefcbb507516c49d1db41c40471
- https://git.kernel.org/stable/c/21a301f12d18797bf889c15497f922edfdaece3a
- https://git.kernel.org/stable/c/aeb7255531ba4a5c3a64938577170d08b78de399
- https://git.kernel.org/stable/c/eae4bf4107571283031db96ce132e951615e2ae4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43368.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43368
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
