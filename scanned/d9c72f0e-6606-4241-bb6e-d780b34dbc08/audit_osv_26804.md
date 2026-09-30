# [H] ubifs: Fix memleak when insert_old_idx() failed

## Summary
Severity: High
Advisory: CVE-2023-54050
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54050
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: Fix memleak when insert_old_idx() failed

Following process will cause a memleak for copied up znode:

dirty_cow_znode
  zn = copy_znode(c, znode);
  err = insert_old_idx(c, zbr->lnum, zbr->offs);
  if (unlikely(err))
     return ERR_PTR(err);   // No one refers to zn.

Fetch a reproducer in [Link].

Function copy_znode() is split into 2 parts: resource allocation
and znode replacement, insert_old_idx() is split in similar way,
so resource cleanup could be done in error handling path without
corrupting metadata(mem & disk).
It's okay that old index inserting is put behind of add_idx_dirt(),
old index is used in layout_leb_in_gaps(), so the two processes do
not depend on each other.

## References
- https://git.kernel.org/stable/c/3ae75f82c33fa1b4ca2006b55c84f4ef4a428d4d
- https://git.kernel.org/stable/c/66e9f2fb3e753f820bec2a98e8c6387029988320
- https://git.kernel.org/stable/c/6f2eee5457bc48b0426dedfd78cdbdea241a6edb
- https://git.kernel.org/stable/c/79079cebbeed624b9d01cfcf1e3254ae1a1f6e14
- https://git.kernel.org/stable/c/a6da0ab9847779e05a7416c7a98148b549de69ef
- https://git.kernel.org/stable/c/b5fda08ef213352ac2df7447611eb4d383cce929
- https://git.kernel.org/stable/c/cc29c7216d7f057eb0613b97dc38c7e1962a88d2
- https://git.kernel.org/stable/c/ef9aac603659e9ffe7d69ae16e3f0fc0991a965b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54050.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54050
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
