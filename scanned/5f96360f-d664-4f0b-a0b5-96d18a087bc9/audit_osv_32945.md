# [H] fs: export anon_inode_make_secure_inode() and fix secretmem LSM bypass

## Summary
Severity: High
Advisory: CVE-2025-38396
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38396
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.146, >=6.2.0 <6.6.97, >=6.7.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: export anon_inode_make_secure_inode() and fix secretmem LSM bypass

Export anon_inode_make_secure_inode() to allow KVM guest_memfd to create
anonymous inodes with proper security context. This replaces the current
pattern of calling alloc_anon_inode() followed by
inode_init_security_anon() for creating security context manually.

This change also fixes a security regression in secretmem where the
S_PRIVATE flag was not cleared after alloc_anon_inode(), causing
LSM/SELinux checks to be bypassed for secretmem file descriptors.

As guest_memfd currently resides in the KVM module, we need to export this
symbol for use outside the core kernel. In the future, guest_memfd might be
moved to core-mm, at which point the symbols no longer would have to be
exported. When/if that happens is still unclear.

## References
- https://git.kernel.org/stable/c/66d29d757c968d2bee9124816da5d718eb352959
- https://git.kernel.org/stable/c/6ca45ea48530332a4ba09595767bd26d3232743b
- https://git.kernel.org/stable/c/cbe4134ea4bc493239786220bd69cb8a13493190
- https://git.kernel.org/stable/c/e3eed01347721cd7a8819568161c91d538fbf229
- https://git.kernel.org/stable/c/f94c422157f3e43dd31990567b3e5d54b3e5b32b
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38396.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38396
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
