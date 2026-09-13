# [H] smb: Log an error when close_all_cached_dirs fails

## Summary
Severity: High
Advisory: CVE-2025-38321
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38321
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: Log an error when close_all_cached_dirs fails

Under low-memory conditions, close_all_cached_dirs() can't move the
dentries to a separate list to dput() them once the locks are dropped.
This will result in a "Dentry still in use" error, so add an error
message that makes it clear this is what happened:

[  495.281119] CIFS: VFS: \\otters.example.com\share Out of memory while dropping dentries
[  495.281595] ------------[ cut here ]------------
[  495.281887] BUG: Dentry ffff888115531138{i=78,n=/}  still in use (2) [unmount of cifs cifs]
[  495.282391] WARNING: CPU: 1 PID: 2329 at fs/dcache.c:1536 umount_check+0xc8/0xf0

Also, bail out of looping through all tcons as soon as a single
allocation fails, since we're already in trouble, and kmalloc() attempts
for subseqeuent tcons are likely to fail just like the first one did.

## References
- https://git.kernel.org/stable/c/43f26094d6702e494e800532c3f1606e7a68eb30
- https://git.kernel.org/stable/c/4479db143390bdcadc1561292aab579cdfa9f6c6
- https://git.kernel.org/stable/c/a2182743a8b4969481f64aec4908ff162e8a206c
- https://git.kernel.org/stable/c/b8ced2b9a23a1a2c1e0ed8d0d02512e51bdf38da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38321.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38321
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
