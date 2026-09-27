# [H] orangefs: fix xattr related buffer overflow...

## Summary
Severity: High
Advisory: CVE-2025-40306
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40306
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

orangefs: fix xattr related buffer overflow...

Willy Tarreau <w@1wt.eu> forwarded me a message from
Disclosure <disclosure@aisle.com> with the following
warning:

> The helper `xattr_key()` uses the pointer variable in the loop condition
> rather than dereferencing it. As `key` is incremented, it remains non-NULL
> (until it runs into unmapped memory), so the loop does not terminate on
> valid C strings and will walk memory indefinitely, consuming CPU or hanging
> the thread.

I easily reproduced this with setfattr and getfattr, causing a kernel
oops, hung user processes and corrupted orangefs files. Disclosure
sent along a diff (not a patch) with a suggested fix, which I based
this patch on.

After xattr_key started working right, xfstest generic/069 exposed an
xattr related memory leak that lead to OOM. xattr_key returns
a hashed key.  When adding xattrs to the orangefs xattr cache, orangefs
used hash_add, a kernel hashing macro. hash_add also hashes the key using
hash_log which resulted in additions to the xattr cache going to the wrong
hash bucket. generic/069 tortures a single file and orangefs does a
getattr for the xattr "security.capability" every time. Orangefs
negative caches on xattrs which includes a kmalloc. Since adds to the
xattr cache were going to the wrong bucket, every getattr for
"security.capability" resulted in another kmalloc, none of which were
ever freed.

I changed the two uses of hash_add to hlist_add_head instead
and the memory leak ceased and generic/069 quit throwing furniture.

## References
- https://git.kernel.org/stable/c/025e880759c279ec64d0f754fe65bf45961da864
- https://git.kernel.org/stable/c/15afebb9597449c444801d1ff0b8d8b311f950ab
- https://git.kernel.org/stable/c/9127d1e90c90e5960c8bc72a4ce2c209691a7021
- https://git.kernel.org/stable/c/bc812574de633cf9a9ad6974490e45f6a4bb5126
- https://git.kernel.org/stable/c/c2ca015ac109fd743fdde27933d59dc5ad46658e
- https://git.kernel.org/stable/c/c6564ff6b53c9a8dc786b6f1c51ae7688273f931
- https://git.kernel.org/stable/c/e09a096104fc65859422817fb2211f35855983fe
- https://git.kernel.org/stable/c/ef892d2bf4f3fa2c8de1677dd307e678bdd3d865
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40306.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40306
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
