# [H] VFS: fix possible failure to unlock in nfsd4_create_file()

## Summary
Severity: High
Advisory: CVE-2026-53244
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53244
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

VFS: fix possible failure to unlock in nfsd4_create_file()

atomic_create() in fs/namei.c drops the reference to the dentry
when it returns an error.
This behaviour was imported into dentry_create() so that it
will drop the reference if an error is returned from atomic_create(),
though not if vfs_create() returns an error (in the case where
->atomic_create is not supported).

The caller - nfsd4_create_file() - is made aware of this by checking
path->dentry, which will either be a counted reference to a dentry, or
an error pointer.

However the change to use start_creating()/end_creating() (which landed
shortly before the dentry_create() change landed, though was likely
developed around the same time) means that nfsd4_create_file() *needs* a
valid dentry so that it can unlock the parent.

The net result is that if NFSD exports a filesystem which uses
->atomic_create, and if a call to ->atomic_create returns an error, then
nfsd4_create_file() will pass an error pointer to end_creating()
and the parent will not be unlocked.

Fix this by changing dentry_create() to make sure path->dentry is always
a valid dentry, never an error-pointer.  The actual error is already
returned a different way.

Note that if ->atomic_create() returns a different dentry (which may not
be possible in practice) we are guaranteed (because it is only ever
provided by d_spliace_alias()) that it will have the same d_parent and
so it will have the same effect when passed to end_creating().

## References
- https://git.kernel.org/stable/c/e824bbd4d224cce4b5fb59cc9dcd3447fe0b7e44
- https://git.kernel.org/stable/c/ee1f40759a50b1800c98c1c369afd5b3e44ad987
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53244.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53244
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
