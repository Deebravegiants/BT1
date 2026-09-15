# [M] ubifs: Free memory for tmpfile name

## Summary
Severity: Medium
Advisory: CVE-2023-53276
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53276
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.14.315, >=4.15.0 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: Free memory for tmpfile name

When opening a ubifs tmpfile on an encrypted directory, function
fscrypt_setup_filename allocates memory for the name that is to be
stored in the directory entry, but after the name has been copied to the
directory entry inode, the memory is not freed.

When running kmemleak on it we see that it is registered as a leak. The
report below is triggered by a simple program 'tmpfile' just opening a
tmpfile:

  unreferenced object 0xffff88810178f380 (size 32):
    comm "tmpfile", pid 509, jiffies 4294934744 (age 1524.742s)
    backtrace:
      __kmem_cache_alloc_node
      __kmalloc
      fscrypt_setup_filename
      ubifs_tmpfile
      vfs_tmpfile
      path_openat

Free this memory after it has been copied to the inode.

## References
- https://git.kernel.org/stable/c/107d481642c356a5668058066360fc473911e628
- https://git.kernel.org/stable/c/1e43d4284bdc3bd34bd770fea13910ac37ab0618
- https://git.kernel.org/stable/c/1fb815b38bb31d6af9bd0540b8652a0d6fe6cfd3
- https://git.kernel.org/stable/c/29738e1bcc799dd754711d4e4aab967f0c018175
- https://git.kernel.org/stable/c/823f554747f8aafaa965fb2f3ae794110ed429ef
- https://git.kernel.org/stable/c/8ad8c67a897e68426e85990ebfe0a7d1f71fc79f
- https://git.kernel.org/stable/c/b8f444a4fadfb5070ed7e298e0a5ceb4a18014f3
- https://git.kernel.org/stable/c/ce840284929b75dbbf062e0ce7fcb78a63b08b5e
- https://git.kernel.org/stable/c/fd197308c0e4f738c7ea687d5332035c5753881c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53276.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53276
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
