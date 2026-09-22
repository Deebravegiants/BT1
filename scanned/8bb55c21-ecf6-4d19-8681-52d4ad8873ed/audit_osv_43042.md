# [H] cachefiles: Fix double unlock in nomem_d_alloc error path

## Summary
Severity: High
Advisory: CVE-2026-72368
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72368
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cachefiles: Fix double unlock in nomem_d_alloc error path

When start_creating() fails and returns -ENOMEM, it has already
released the parent directory lock in __start_dirop():

    static struct dentry *__start_dirop(...)
    {
        ...
        inode_lock_nested(dir, I_MUTEX_PARENT);
        dentry = lookup_one_qstr_excl(name, parent, lookup_flags);
        if (IS_ERR(dentry))
            inode_unlock(dir);  <-- Lock released on error
        return dentry;
    }

However, the nomem_d_alloc error path in cachefiles_get_directory()
unconditionally calls inode_unlock(d_inode(dir)) again, causing a
double unlock that corrupts the rwsem state.

This is a leftover from commit 7ab96df840e60 which replaced manual
locking with start_creating() but failed to update the nomem_d_alloc
path (while correctly updating mkdir_error and lookup_error paths).

## References
- https://git.kernel.org/stable/c/26757dac15175f2a42e3537f1ba86e62456d48f1
- https://git.kernel.org/stable/c/8c256fba2b46020004201c500b2a1fbc707a33ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72368.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72368
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
