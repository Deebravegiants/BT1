# [H] btrfs: fix uninitialized pointer free on read_alloc_one_name() error

## Summary
Severity: High
Advisory: CVE-2024-50087
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50087
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.114, >=6.2.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix uninitialized pointer free on read_alloc_one_name() error

The function read_alloc_one_name() does not initialize the name field of
the passed fscrypt_str struct if kmalloc fails to allocate the
corresponding buffer.  Thus, it is not guaranteed that
fscrypt_str.name is initialized when freeing it.

This is a follow-up to the linked patch that fixes the remaining
instances of the bug introduced by commit e43eec81c516 ("btrfs: use
struct qstr instead of name and namelen pairs").

## References
- https://git.kernel.org/stable/c/1ec28de5e476913ae51f909660b4447eddb28838
- https://git.kernel.org/stable/c/2ab5e243c2266c841e0f6904fad1514b18eaf510
- https://git.kernel.org/stable/c/7fc7c47b9ba0cf2d192f2117a64b24881b0b577f
- https://git.kernel.org/stable/c/b37de9491f140a0ff125c27dd1050185c3accbc1
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50087.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
