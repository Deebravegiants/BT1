# [H] NFS: Fix a race when updating an existing write

## Summary
Severity: High
Advisory: CVE-2025-39697
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39697
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.242, >=5.11.0 <5.15.191, >=5.16.0 <6.1.150, >=6.2.0 <6.6.104, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Fix a race when updating an existing write

After nfs_lock_and_join_requests() tests for whether the request is
still attached to the mapping, nothing prevents a call to
nfs_inode_remove_request() from succeeding until we actually lock the
page group.
The reason is that whoever called nfs_inode_remove_request() doesn't
necessarily have a lock on the page group head.

So in order to avoid races, let's take the page group lock earlier in
nfs_lock_and_join_requests(), and hold it across the removal of the
request in nfs_inode_remove_request().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/0ff42a32784e0f2cb46a46da8e9f473538c13e1b
- https://git.kernel.org/stable/c/181feb41f0b268e6288bf9a7b984624d7fe2031d
- https://git.kernel.org/stable/c/202a3432d21ac060629a760fff3b0a39859da3ea
- https://git.kernel.org/stable/c/76d2e3890fb169168c73f2e4f8375c7cc24a765e
- https://git.kernel.org/stable/c/92278ae36935a54e65fef9f8ea8efe7e80481ace
- https://git.kernel.org/stable/c/c32e3c71aaa1c1ba05da88605e2ddd493c58794f
- https://git.kernel.org/stable/c/f230d40147cc37eb3aef4d50e2e2c06ea73d9a77
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39697.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
