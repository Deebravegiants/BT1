# [H] ext4: fix invalid free tracking in ext4_xattr_move_to_block()

## Summary
Severity: High
Advisory: CVE-2023-54062
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54062
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.315, >=4.15.0 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.112, >=5.16.0 <6.1.29, >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix invalid free tracking in ext4_xattr_move_to_block()

In ext4_xattr_move_to_block(), the value of the extended attribute
which we need to move to an external block may be allocated by
kvmalloc() if the value is stored in an external inode.  So at the end
of the function the code tried to check if this was the case by
testing entry->e_value_inum.

However, at this point, the pointer to the xattr entry is no longer
valid, because it was removed from the original location where it had
been stored.  So we could end up calling kvfree() on a pointer which
was not allocated by kvmalloc(); or we could also potentially leak
memory by not freeing the buffer when it should be freed.  Fix this by
storing whether it should be freed in a separate variable.

## References
- https://git.kernel.org/stable/c/1a8822343e67432b658145d2760a524c884da9d4
- https://git.kernel.org/stable/c/76887be2a96193cd11be818551b8934ecdb3123f
- https://git.kernel.org/stable/c/8beaa3cb293a8f7bacf711cf52201d59859dbc40
- https://git.kernel.org/stable/c/a18670395e5f28acddeca037c5e4bd2ea961b70a
- https://git.kernel.org/stable/c/b2fab1807d26acd1c6115b95b5eddd697d84751b
- https://git.kernel.org/stable/c/b87c7cdf2bed4928b899e1ce91ef0d147017ba45
- https://git.kernel.org/stable/c/ba04d6af5ac440a6d5a2d35dc1d8e2cb0323550a
- https://git.kernel.org/stable/c/c5fa4eedddd1c8342ce533cb401c0e693e55b4e3
- https://git.kernel.org/stable/c/f30f3391d089dc91aef91d08f4b04a6c0df2b067
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54062.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54062
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
