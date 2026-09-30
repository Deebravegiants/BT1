# [H] memcg: protect concurrent access to mem_cgroup_idr

## Summary
Severity: High
Advisory: CVE-2024-43892
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-43892
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.46, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

memcg: protect concurrent access to mem_cgroup_idr

Commit 73f576c04b94 ("mm: memcontrol: fix cgroup creation failure after
many small jobs") decoupled the memcg IDs from the CSS ID space to fix the
cgroup creation failures.  It introduced IDR to maintain the memcg ID
space.  The IDR depends on external synchronization mechanisms for
modifications.  For the mem_cgroup_idr, the idr_alloc() and idr_replace()
happen within css callback and thus are protected through cgroup_mutex
from concurrent modifications.  However idr_remove() for mem_cgroup_idr
was not protected against concurrency and can be run concurrently for
different memcgs when they hit their refcnt to zero.  Fix that.

We have been seeing list_lru based kernel crashes at a low frequency in
our fleet for a long time.  These crashes were in different part of
list_lru code including list_lru_add(), list_lru_del() and reparenting
code.  Upon further inspection, it looked like for a given object (dentry
and inode), the super_block's list_lru didn't have list_lru_one for the
memcg of that object.  The initial suspicions were either the object is
not allocated through kmem_cache_alloc_lru() or somehow
memcg_list_lru_alloc() failed to allocate list_lru_one() for a memcg but
returned success.  No evidence were found for these cases.

Looking more deeply, we started seeing situations where valid memcg's id
is not present in mem_cgroup_idr and in some cases multiple valid memcgs
have same id and mem_cgroup_idr is pointing to one of them.  So, the most
reasonable explanation is that these situations can happen due to race
between multiple idr_remove() calls or race between
idr_alloc()/idr_replace() and idr_remove().  These races are causing
multiple memcgs to acquire the same ID and then offlining of one of them
would cleanup list_lrus on the system for all of them.  Later access from
other memcgs to the list_lru cause crashes due to missing list_lru_one.

## References
- https://git.kernel.org/stable/c/37a060b64ae83b76600d187d76591ce488ab836b
- https://git.kernel.org/stable/c/51c0b1bb7541f8893ec1accba59eb04361a70946
- https://git.kernel.org/stable/c/56fd70f4aa8b82199dbe7e99366b1fd7a04d86fb
- https://git.kernel.org/stable/c/912736a0435ef40e6a4ae78197ccb5553cb80b05
- https://git.kernel.org/stable/c/9972605a238339b85bd16b084eed5f18414d22db
- https://git.kernel.org/stable/c/e6cc9ff2ac0b5df9f25eb790934c3104f6710278
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43892.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43892
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
