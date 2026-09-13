# [H] ext4: make sure the first directory block is not a hole

## Summary
Severity: High
Advisory: CVE-2024-42304
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42304
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.320, >=4.20.0 <5.4.282, >=5.3.0 <5.10.224, >=5.5.0 <5.15.165, >=5.11.0 <6.1.103, >=5.16.0 <6.6.44, >=6.2.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: make sure the first directory block is not a hole

The syzbot constructs a directory that has no dirblock but is non-inline,
i.e. the first directory block is a hole. And no errors are reported when
creating files in this directory in the following flow.

    ext4_mknod
     ...
      ext4_add_entry
        // Read block 0
        ext4_read_dirblock(dir, block, DIRENT)
          bh = ext4_bread(NULL, inode, block, 0)
          if (!bh && (type == INDEX || type == DIRENT_HTREE))
          // The first directory block is a hole
          // But type == DIRENT, so no error is reported.

After that, we get a directory block without '.' and '..' but with a valid
dentry. This may cause some code that relies on dot or dotdot (such as
make_indexed_dir()) to crash.

Therefore when ext4_read_dirblock() finds that the first directory block
is a hole report that the filesystem is corrupted and return an error to
avoid loading corrupted data from disk causing something bad.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/299bc6ffa57e04e74c6cce866d6c0741fb4897a1
- https://git.kernel.org/stable/c/9771e3d8365ae1dd5e8846a204cb9af14e3e656a
- https://git.kernel.org/stable/c/b609753cbbd38f8c0affd4956c0af178348523ac
- https://git.kernel.org/stable/c/c3893d9de8ee153baac56d127d844103488133b5
- https://git.kernel.org/stable/c/d81d7e347d1f1f48a5634607d39eb90c161c8afe
- https://git.kernel.org/stable/c/de2a011a13a46468a6e8259db58b1b62071fe136
- https://git.kernel.org/stable/c/e02f9941e8c011aa3eafa799def6a134ce06bcfa
- https://git.kernel.org/stable/c/f9ca51596bbfd0f9c386dd1c613c394c78d9e5e6
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42304.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42304
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
