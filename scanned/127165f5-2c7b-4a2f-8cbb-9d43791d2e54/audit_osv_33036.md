# [H] drm/panthor: Fix UAF in panthor_gem_create_with_handle() debugfs code

## Summary
Severity: High
Advisory: CVE-2025-38596
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38596
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Fix UAF in panthor_gem_create_with_handle() debugfs code

The object is potentially already gone after the drm_gem_object_put().
In general the object should be fully constructed before calling
drm_gem_handle_create(), except the debugfs tracking uses a separate
lock and list and separate flag to denotate whether the object is
actually initialized.

Since I'm touching this all anyway simplify this by only adding the
object to the debugfs when it's ready for that, which allows us to
delete that separate flag. panthor_gem_debugfs_bo_rm() already checks
whether we've actually been added to the list or this is some error
path cleanup.

v2: Fix build issues for !CONFIG_DEBUGFS (Adrián)

v3: Add linebreak and remove outdated comment (Liviu)

## References
- https://git.kernel.org/stable/c/5f2be12442db6a2904e6e31b0e3b5ad5aebf868b
- https://git.kernel.org/stable/c/fe69a391808404977b1f002a6e7447de3de7a88e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38596.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38596
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
