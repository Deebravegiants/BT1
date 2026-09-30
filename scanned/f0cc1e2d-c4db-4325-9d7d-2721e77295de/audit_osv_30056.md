# [H] ext4: avoid use-after-free in ext4_ext_show_leaf()

## Summary
Severity: High
Advisory: CVE-2024-49889
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49889
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: avoid use-after-free in ext4_ext_show_leaf()

In ext4_find_extent(), path may be freed by error or be reallocated, so
using a previously saved *ppath may have been freed and thus may trigger
use-after-free, as follows:

ext4_split_extent
  path = *ppath;
  ext4_split_extent_at(ppath)
  path = ext4_find_extent(ppath)
  ext4_split_extent_at(ppath)
    // ext4_find_extent fails to free path
    // but zeroout succeeds
  ext4_ext_show_leaf(inode, path)
    eh = path[depth].p_hdr
    // path use-after-free !!!

Similar to ext4_split_extent_at(), we use *ppath directly as an input to
ext4_ext_show_leaf(). Fix a spelling error by the way.

Same problem in ext4_ext_handle_unwritten_extents(). Since 'path' is only
used in ext4_ext_show_leaf(), remove 'path' and use *ppath directly.

This issue is triggered only when EXT_DEBUG is defined and therefore does
not affect functionality.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/2eba3b0cc5b8de624918d21f32b5b8db59a90b39
- https://git.kernel.org/stable/c/34b2096380ba475771971a778a478661a791aa15
- https://git.kernel.org/stable/c/4999fed877bb64e3e7f9ab9996de2ca983c41928
- https://git.kernel.org/stable/c/4e2524ba2ca5f54bdbb9e5153bea00421ef653f5
- https://git.kernel.org/stable/c/8b114f2cc7dd5d36729d040b68432fbd0f0a8868
- https://git.kernel.org/stable/c/b0cb4561fc4284d04e69c8a66c8504928ab2484e
- https://git.kernel.org/stable/c/d483c7cc1796bd6a80e7b3a8fd494996260f6b67
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49889.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49889
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
