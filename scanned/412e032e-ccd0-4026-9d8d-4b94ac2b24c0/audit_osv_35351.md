# [H] drm/i915/gem: Zero-initialize the eb.vma array in i915_gem_do_execbuffer

## Summary
Severity: High
Advisory: CVE-2025-71130
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71130
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/gem: Zero-initialize the eb.vma array in i915_gem_do_execbuffer

Initialize the eb.vma array with values of 0 when the eb structure is
first set up. In particular, this sets the eb->vma[i].vma pointers to
NULL, simplifying cleanup and getting rid of the bug described below.

During the execution of eb_lookup_vmas(), the eb->vma array is
successively filled up with struct eb_vma objects. This process includes
calling eb_add_vma(), which might fail; however, even in the event of
failure, eb->vma[i].vma is set for the currently processed buffer.

If eb_add_vma() fails, eb_lookup_vmas() returns with an error, which
prompts a call to eb_release_vmas() to clean up the mess. Since
eb_lookup_vmas() might fail during processing any (possibly not first)
buffer, eb_release_vmas() checks whether a buffer's vma is NULL to know
at what point did the lookup function fail.

In eb_lookup_vmas(), eb->vma[i].vma is set to NULL if either the helper
function eb_lookup_vma() or eb_validate_vma() fails. eb->vma[i+1].vma is
set to NULL in case i915_gem_object_userptr_submit_init() fails; the
current one needs to be cleaned up by eb_release_vmas() at this point,
so the next one is set. If eb_add_vma() fails, neither the current nor
the next vma is set to NULL, which is a source of a NULL deref bug
described in the issue linked in the Closes tag.

When entering eb_lookup_vmas(), the vma pointers are set to the slab
poison value, instead of NULL. This doesn't matter for the actual
lookup, since it gets overwritten anyway, however the eb_release_vmas()
function only recognizes NULL as the stopping value, hence the pointers
are being set to NULL as they go in case of intermediate failure. This
patch changes the approach to filling them all with NULL at the start
instead, rather than handling that manually during failure.

(cherry picked from commit 08889b706d4f0b8d2352b7ca29c2d8df4d0787cd)

## References
- https://git.kernel.org/stable/c/0336188cc85d0eab8463bd1bbd4ded4e9602de8b
- https://git.kernel.org/stable/c/24d55ac8e31d2f8197bfad71ffcb3bae21ed7117
- https://git.kernel.org/stable/c/25d69e07770745992387c016613fd7ac8eaf9893
- https://git.kernel.org/stable/c/4fe2bd195435e71c117983d87f278112c5ab364c
- https://git.kernel.org/stable/c/63f23aa2fbb823c8b15a29269fde220d227ce5b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71130.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71130
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
