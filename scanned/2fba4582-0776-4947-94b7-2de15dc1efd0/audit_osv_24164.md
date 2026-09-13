# [H] fs: fix UAF/GPF bug in nilfs_mdt_destroy

## Summary
Severity: High
Advisory: CVE-2022-50367
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50367
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.218, >=5.5.0 <5.10.148, >=5.11.0 <5.15.73, >=5.16.0 <5.19.15, >=5.20.0 <6.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: fix UAF/GPF bug in nilfs_mdt_destroy

In alloc_inode, inode_init_always() could return -ENOMEM if
security_inode_alloc() fails, which causes inode->i_private
uninitialized. Then nilfs_is_metadata_file_inode() returns
true and nilfs_free_inode() wrongly calls nilfs_mdt_destroy(),
which frees the uninitialized inode->i_private
and leads to crashes(e.g., UAF/GPF).

Fix this by moving security_inode_alloc just prior to
this_cpu_inc(nr_inodes)

## References
- https://git.kernel.org/stable/c/1e555c3ed1fce4b278aaebe18a64a934cece57d8
- https://git.kernel.org/stable/c/2a96b532098284ecf8e4849b8b9e5fc7a28bdee9
- https://git.kernel.org/stable/c/2e488f13755ffbb60f307e991b27024716a33b29
- https://git.kernel.org/stable/c/64b79e632869ad3ef6c098a4731d559381da1115
- https://git.kernel.org/stable/c/70e4f70d54e0225f91814e8610477d65f33cefe4
- https://git.kernel.org/stable/c/81de80330fa6907aec32eb54c5619059e6e36452
- https://git.kernel.org/stable/c/c0aa76b0f17f59dd9c9d3463550a2986a1d592e4
- https://git.kernel.org/stable/c/d1ff475d7c83289d0a7faef346ea3bbf90818bad
- https://git.kernel.org/stable/c/ec2aab115eb38ac4992ea2fcc2a02fbe7af5cf48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50367.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50367
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
