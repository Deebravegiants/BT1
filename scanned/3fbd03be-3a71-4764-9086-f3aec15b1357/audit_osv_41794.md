# [H] drm/gem: fix race between change_handle and handle_delete

## Summary
Severity: High
Advisory: CVE-2026-63885
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63885
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.32 <6.18.35, >=7.0.9 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/gem: fix race between change_handle and handle_delete

drm_gem_change_handle_ioctl leaves the old handle live in the IDR
during the window between spin_unlock(table_lock) and the final
spin_lock(table_lock). A concurrent drm_gem_handle_delete on the old
handle succeeds in this window, decrements handle_count to 0, and frees
the GEM object while the new handle's IDR entry still references it.

NULL the old handle's IDR entry before dropping table_lock so that any
concurrent GEM_CLOSE on the old handle sees NULL and returns -EINVAL.
Restore the old entry on the prime-bookkeeping error path.

## References
- https://git.kernel.org/stable/c/0dfa42cfe4dbe114533480503934f43e33c1e83d
- https://git.kernel.org/stable/c/7164d78559b0ff29931a366a840a9e5dd53d4b7c
- https://git.kernel.org/stable/c/cde2c9257cbe8463b9dcf7b1075177b72b5fd938
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63885.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63885
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
