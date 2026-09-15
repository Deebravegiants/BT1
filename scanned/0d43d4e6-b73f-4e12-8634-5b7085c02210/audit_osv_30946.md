# [H] drm/amd/display: Fix handling of plane refcount

## Summary
Severity: High
Advisory: CVE-2024-56775
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56775
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix handling of plane refcount

[Why]
The mechanism to backup and restore plane states doesn't maintain
refcount, which can cause issues if the refcount of the plane changes
in between backup and restore operations, such as memory leaks if the
refcount was supposed to go down, or double frees / invalid memory
accesses if the refcount was supposed to go up.

[How]
Cache and re-apply current refcount when restoring plane states.

## References
- https://git.kernel.org/stable/c/27227a234c1487cb7a684615f0749c455218833a
- https://git.kernel.org/stable/c/8cb2f6793845f135b28361ba8e96901cae3e5790
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56775.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56775
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
