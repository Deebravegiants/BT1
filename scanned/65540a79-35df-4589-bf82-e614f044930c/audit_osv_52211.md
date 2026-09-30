# [H] CVE-2021-47200

## Summary
Severity: High
Advisory: CVE-2021-47200
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47200
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/prime: Fix use after free in mmap with drm_gem_ttm_mmap

drm_gem_ttm_mmap() drops a reference to the gem object on success. If
the gem object's refcount == 1 on entry to drm_gem_prime_mmap(), that
drop will free the gem object, and the subsequent drm_gem_object_get()
will be a UAF. Fix by grabbing a reference before calling the mmap
helper.

This issue was forseen when the reference dropping was adding in
commit 9786b65bc61ac ("drm/ttm: fix mmap refcounting"):
  "For that to work properly the drm_gem_object_get() call in
  drm_gem_ttm_mmap() must be moved so it happens before calling
  obj->funcs->mmap(), otherwise the gem refcount would go down
  to zero."

## References
- https://git.kernel.org/stable/c/4f8e469a2384dfa4047145b0093126462cbb6dc0
- https://git.kernel.org/stable/c/8244a3bc27b3efd057da154b8d7e414670d5044f
