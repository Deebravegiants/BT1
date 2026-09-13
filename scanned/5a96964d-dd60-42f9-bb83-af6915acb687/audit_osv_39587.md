# [H] drm: Set old handle to NULL before prime swap in change_handle

## Summary
Severity: High
Advisory: CVE-2026-46215
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46215
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: Set old handle to NULL before prime swap in change_handle

There was a potential race condition in change_handle. The ioctl
briefly had a single object with two idr entries; a concurrent
gem_close could delete the object and remove one of the handles
while leaving the other one dangling, which could subsequently
be dereferenced for a use-after-free.

To fix this, do the same dance that gem_close itself does.
(f6cd7daecff5 drm: Release driver references to handle before making it available again)
First idr_replace the old handle to NULL. Later, if the prime
operations are successful, actually close it.

create_tail required a similar dance to avoid a similar problem.
(bd46cece51a3 drm/gem: Fix race in drm_gem_handle_create_tail())
It idr_allocs the new handle with NULL, then swaps in the correct
object later to avoid races. We don't need to do that here, since
the only operations that could race are drm_prime, and
change_handle holds the prime lock for the entire duration.

v2: cleanups of error paths

## References
- https://git.kernel.org/stable/c/5e28b7b94408897e41c63477aabc9e1db439bc8c
- https://git.kernel.org/stable/c/61bd96d3e5472c253f9c1ab77608f0c8aaa9d025
- https://git.kernel.org/stable/c/672464dd53231509c9c771110798c56d4660e19e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46215.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46215
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/0xCyberstan/CVE-2026-46215-POC
