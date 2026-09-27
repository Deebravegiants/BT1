# [H] drm/xe/dma-buf: handle empty bo and UAF races

## Summary
Severity: High
Advisory: CVE-2026-52951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52951
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/dma-buf: handle empty bo and UAF races

There look to be some nasty races here when triggering the
invalidate_mappings hook:

1) We do xe_bo_alloc() followed by the attach, before the actual full bo
   init step in xe_dma_buf_init_obj(). However the bo is visible on the
   attachments list after the attach.  This is bad since exporter driver,
   say amdgpu, can at any time call back into our invalidate_mappings hook,
   with an empty/bogus bo, leading to potential bugs/crashes.

2) Similar to 1) but here we get a UAF, when the invalidate_mappings
   hook is triggered. For example, we get as far as xe_bo_init_locked()
   but this fails in some way. But here the bo will be freed on error, but
   we still have it attached from dma-buf pov, so if the
   invalidate_mappings is now triggered then the bo we access is gone and
   we trigger UAF and more bugs/crashes.

To fix this, move the attach step until after we actually have a fully
set up buffer object. Note that the bo is not published to userspace
until later, so not sure what the comment "Don't publish the bo
until we have a valid attachment", is referring to.

We have at least two different customers reporting hitting a NULL ptr
deref in evict_flags when importing something from amdgpu, followed by
triggering the evict flow. Hit rate is also pretty low, which would
hint at some kind of race, so something like 1) or 2) might explain
this.

v2:
  - Shuffle the order of the ops slightly (no functional change)
  - Improve the comment to better explain the ordering (Matt B)

(cherry picked from commit af1f2ad0c59fe4e2f924c526f66e968289d77971)

## References
- https://git.kernel.org/stable/c/20a99ea1e2fd720856d6ba497ff26b82c604751f
- https://git.kernel.org/stable/c/981bedbbe61364fcc3a3b87ebaf648a66cd07108
- https://git.kernel.org/stable/c/9894731e513019df22a29e5c52f1c98890355ff1
- https://git.kernel.org/stable/c/c473ae25421fddc3dde247ba7b85225b10641d09
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52951.json
- https://access.redhat.com/security/cve/CVE-2026-52951
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52951.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52951
- https://bugzilla.redhat.com/show_bug.cgi?id=2492353
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
