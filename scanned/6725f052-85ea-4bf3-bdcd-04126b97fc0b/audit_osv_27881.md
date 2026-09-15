# [H] ceph: prevent use-after-free in encode_cap_msg()

## Summary
Severity: High
Advisory: CVE-2024-26689
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26689
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: prevent use-after-free in encode_cap_msg()

In fs/ceph/caps.c, in encode_cap_msg(), "use after free" error was
caught by KASAN at this line - 'ceph_buffer_get(arg->xattr_buf);'. This
implies before the refcount could be increment here, it was freed.

In same file, in "handle_cap_grant()" refcount is decremented by this
line - 'ceph_buffer_put(ci->i_xattrs.blob);'. It appears that a race
occurred and resource was freed by the latter line before the former
line could increment it.

encode_cap_msg() is called by __send_cap() and __send_cap() is called by
ceph_check_caps() after calling __prep_cap(). __prep_cap() is where
arg->xattr_buf is assigned to ci->i_xattrs.blob. This is the spot where
the refcount must be increased to prevent "use after free" error.

## References
- https://git.kernel.org/stable/c/70e329b440762390258a6fe8c0de93c9fdd56c77
- https://git.kernel.org/stable/c/7958c1bf5b03c6f1f58e724dbdec93f8f60b96fc
- https://git.kernel.org/stable/c/8180d0c27b93a6eb60da1b08ea079e3926328214
- https://git.kernel.org/stable/c/ae20db45e482303a20e56f2db667a9d9c54ac7e7
- https://git.kernel.org/stable/c/cda4672da1c26835dcbd7aec2bfed954eda9b5ef
- https://git.kernel.org/stable/c/f3f98d7d84b31828004545e29fd7262b9f444139
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26689.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26689
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
