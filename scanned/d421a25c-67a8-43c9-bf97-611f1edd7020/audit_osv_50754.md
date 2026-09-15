# [H] CVE-2020-36788

## Summary
Severity: High
Advisory: CVE-2020-36788
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2020-36788
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/nouveau: avoid a use-after-free when BO init fails

nouveau_bo_init() is backed by ttm_bo_init() and ferries its return code
back to the caller. On failures, ttm_bo_init() invokes the provided
destructor which should de-initialize and free the memory.

Thus, when nouveau_bo_init() returns an error the gem object has already
been released and the memory freed by nouveau_bo_del_ttm().

## References
- https://git.kernel.org/stable/c/bcf34aa5082ee2343574bc3f4d1c126030913e54
- https://git.kernel.org/stable/c/f86e19d918a85492ad1a01fcdc0ad5ecbdac6f96
- https://git.kernel.org/stable/c/548f2ff8ea5e0ce767ae3418d1ec5308990be87d
