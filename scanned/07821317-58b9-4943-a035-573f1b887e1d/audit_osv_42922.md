# [H] ocfs2: reject dinodes with non-canonical i_mode type

## Summary
Severity: High
Advisory: CVE-2026-72160
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72160
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: reject dinodes with non-canonical i_mode type

Patch series "ocfs2: harden inode validators against forged metadata", v2.

This series adds three structural checks to OCFS2 dinode validation so
malformed on-disk fields are rejected before ocfs2_populate_inode() copies
them into the in-core inode.

The checks cover:

  - i_mode values whose type bits do not name a canonical POSIX file
    type;
  - non-device dinodes whose id1.dev1.i_rdev field is non-zero; and
  - non-inline dinodes that claim non-zero i_size while i_clusters is
    zero, covering directories unconditionally and regular files on
    non-sparse volumes.

The normal read path reports these through ocfs2_error(), matching the
existing suballoc-slot, inline-data, chain-list, and refcount checks.  The
online filecheck path uses the same structural predicates but keeps its
own reporting contract, returning OCFS2_FILECHECK_ERR_INVALIDINO instead
of calling ocfs2_error().


This patch (of 3):

ocfs2_validate_inode_block() currently accepts any non-zero i_mode value. 
ocfs2_populate_inode() then copies that mode verbatim into inode->i_mode
and dispatches on i_mode & S_IFMT to the file/dir/symlink/special_file
iops; an unrecognised type falls through to ocfs2_special_file_iops and
init_special_inode().

Reject dinodes whose type bits do not name one of the seven canonical
POSIX file types.  Use fs_umode_to_ftype(), the same generic file-type
conversion helper OCFS2 already uses for directory entries, so the
accepted inode type set matches the kernel file-type vocabulary instead of
open-coding a local switch.

Apply the same structural check to the online filecheck read path. 
filecheck keeps its own error namespace, so it reports malformed i_mode
through the filecheck logger and OCFS2_FILECHECK_ERR_INVALIDINO instead of
calling ocfs2_error(), but it must not allow a malformed dinode to proceed
into ocfs2_populate_inode().

## References
- https://git.kernel.org/stable/c/157d31ef45038d89cd19620105e082d43c8e41e0
- https://git.kernel.org/stable/c/2e3aac33988ef4e4170141db8e995693ea38357c
- https://git.kernel.org/stable/c/4db3b6a2a8ecf2a89d26a4090ace4072c6fad050
- https://git.kernel.org/stable/c/5366a017099c6a3c443be908a05f26fd72af12a1
- https://git.kernel.org/stable/c/82afe13558354390d8a592a5334d5f4fd72c0e5c
- https://git.kernel.org/stable/c/a5b555bcabbb0aff8745ad181768eaf9d964c1ee
- https://git.kernel.org/stable/c/b858f2d57cfc9d57ce61b86051d603dc0ebccd40
- https://git.kernel.org/stable/c/fb024ea29f6cb1f01745e5f2e31646f3acb9aa6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72160.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72160
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
