# [H] fscrypt: Add missing superblock check in find_or_insert_direct_key()

## Summary
Severity: High
Advisory: CVE-2026-68148
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68148
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fscrypt: Add missing superblock check in find_or_insert_direct_key()

The legacy 'fscrypt_direct_keys' table caches master keys that are used
by v1 encryption policies that have FSCRYPT_POLICY_FLAG_DIRECT_KEY.
It's just a global table for all filesystems (since the keys can be
provided by the legacy process-subscribed keyrings mechanism, which
makes it difficult to reuse super_block::s_master_keys).

The entries in it ('struct fscrypt_direct_key') do contain a super_block
pointer, though, for passing to fscrypt_destroy_inline_crypt_key() when
the last inode that references the key is evicted.

However, when finding the fscrypt_direct_key for an inode, we weren't
actually comparing the super_block pointer.  As a result, inodes with
different super_blocks could point to the same fscrypt_direct_key.  That
could extend the lifetime of a fscrypt_direct_key beyond the
super_block it points to, causing a use-after-free later.

Fix this by creating distinct fscrypt_direct_key structs for distinct
super_block structs.

Note that this problem doesn't exist in the v2 policy equivalent
("per-mode keys"), since the data structures there are per super_block.

## References
- https://git.kernel.org/stable/c/330249609b70778094a7a36f5b6bcfa6362121d4
- https://git.kernel.org/stable/c/466f187b501a5ac8e1ea2ccf3ccd5c46108d8830
- https://git.kernel.org/stable/c/95376fe9c145be35566991df99c53134943d992f
- https://git.kernel.org/stable/c/965b5bc8cf5031225e057979ce660fec2bd5fbfc
- https://git.kernel.org/stable/c/b5fa40226e71c17847b9ff2816c6ca4133d0d994
- https://git.kernel.org/stable/c/deff41898a5ae3a47db5fa1896a494aa95efda5d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68148.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68148
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
