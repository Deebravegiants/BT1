# [M] ubifs: Fix memory leak in do_rename

## Summary
Severity: Medium
Advisory: CVE-2023-53396
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53396
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.112, >=5.16.0 <6.1.28, >=5.18.0 <6.2.15, >=6.2.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: Fix memory leak in do_rename

If renaming a file in an encrypted directory, function
fscrypt_setup_filename allocates memory for a file name. This name is
never used, and before returning to the caller the memory for it is not
freed.

When running kmemleak on it we see that it is registered as a leak. The
report below is triggered by a simple program 'rename' that renames a
file in an encrypted directory:

  unreferenced object 0xffff888101502840 (size 32):
    comm "rename", pid 9404, jiffies 4302582475 (age 435.735s)
    backtrace:
      __kmem_cache_alloc_node
      __kmalloc
      fscrypt_setup_filename
      do_rename
      ubifs_rename
      vfs_rename
      do_renameat2

To fix this we can remove the call to fscrypt_setup_filename as it's not
needed.

## References
- https://git.kernel.org/stable/c/3a36d20e012903f45714df2731261fdefac900cb
- https://git.kernel.org/stable/c/43b2f7d690697182beed6f71aa57b7249d3cfc9c
- https://git.kernel.org/stable/c/517ddc0259d7a7231486bdafde8035c478bc4088
- https://git.kernel.org/stable/c/7e264f67b7d6580eff5c2696961039fd05c69258
- https://git.kernel.org/stable/c/9f565752b328fe53c9e42b7d4e4d89a1da63d738
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53396.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53396
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
