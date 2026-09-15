# [H] drm/i915/ttm: fix CCS handling

## Summary
Severity: High
Advisory: CVE-2022-49963
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49963
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/ttm: fix CCS handling

Crucible + recent Mesa seems to sometimes hit:

GEM_BUG_ON(num_ccs_blks > NUM_CCS_BLKS_PER_XFER)

And it looks like we can also trigger this with gem_lmem_swapping, if we
modify the test to use slightly larger object sizes.

Looking closer it looks like we have the following issues in
migrate_copy():

  - We are using plain integer in various places, which we can easily
    overflow with a large object.

  - We pass the entire object size (when the src is lmem) into
    emit_pte() and then try to copy it, which doesn't work, since we
    only have a few fixed sized windows in which to map the pages and
    perform the copy. With an object > 8M we therefore aren't properly
    copying the pages. And then with an object > 64M we trigger the
    GEM_BUG_ON(num_ccs_blks > NUM_CCS_BLKS_PER_XFER).

So it looks like our copy handling for any object > 8M (which is our
CHUNK_SZ) is currently broken on DG2.

Testcase: igt@gem_lmem_swapping
(cherry picked from commit 8676145eb2f53a9940ff70910caf0125bd8a4bc2)

## References
- https://git.kernel.org/stable/c/8d905254162965c8e6be697d82c7dbf5d08f574d
- https://git.kernel.org/stable/c/97434cb55bd884bd268626ec41489f79b261b2d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49963.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49963
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
