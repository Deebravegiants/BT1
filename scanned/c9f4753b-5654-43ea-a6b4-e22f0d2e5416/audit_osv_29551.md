# [H] cgroup/cpuset: Prevent UAF in proc_cpuset_show()

## Summary
Severity: High
Advisory: CVE-2024-43853
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43853
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <4.19.321, >=4.20.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

cgroup/cpuset: Prevent UAF in proc_cpuset_show()

An UAF can happen when /proc/cpuset is read as reported in [1].

This can be reproduced by the following methods:
1.add an mdelay(1000) before acquiring the cgroup_lock In the
 cgroup_path_ns function.
2.$cat /proc/<pid>/cpuset   repeatly.
3.$mount -t cgroup -o cpuset cpuset /sys/fs/cgroup/cpuset/
$umount /sys/fs/cgroup/cpuset/   repeatly.

The race that cause this bug can be shown as below:

(umount)		|	(cat /proc/<pid>/cpuset)
css_release		|	proc_cpuset_show
css_release_work_fn	|	css = task_get_css(tsk, cpuset_cgrp_id);
css_free_rwork_fn	|	cgroup_path_ns(css->cgroup, ...);
cgroup_destroy_root	|	mutex_lock(&cgroup_mutex);
rebind_subsystems	|
cgroup_free_root 	|
			|	// cgrp was freed, UAF
			|	cgroup_path_ns_locked(cgrp,..);

When the cpuset is initialized, the root node top_cpuset.css.cgrp
will point to &cgrp_dfl_root.cgrp. In cgroup v1, the mount operation will
allocate cgroup_root, and top_cpuset.css.cgrp will point to the allocated
&cgroup_root.cgrp. When the umount operation is executed,
top_cpuset.css.cgrp will be rebound to &cgrp_dfl_root.cgrp.

The problem is that when rebinding to cgrp_dfl_root, there are cases
where the cgroup_root allocated by setting up the root for cgroup v1
is cached. This could lead to a Use-After-Free (UAF) if it is
subsequently freed. The descendant cgroups of cgroup v1 can only be
freed after the css is released. However, the css of the root will never
be released, yet the cgroup_root should be freed when it is unmounted.
This means that obtaining a reference to the css of the root does
not guarantee that css.cgrp->root will not be freed.

Fix this problem by using rcu_read_lock in proc_cpuset_show().
As cgroup_root is kfree_rcu after commit d23b5c577715
("cgroup: Make operations on the cgroup root_list RCU safe"),
css->cgroup won't be freed during the critical section.
To call cgroup_path_ns_locked, css_set_lock is needed, so it is safe to
replace task_get_css with task_css.

[1] https://syzkaller.appspot.com/bug?extid=9b1ff7be974a403aa4cd

## References
- https://git.kernel.org/stable/c/10aeaa47e4aa2432f29b3e5376df96d7dac5537a
- https://git.kernel.org/stable/c/1be59c97c83ccd67a519d8a49486b3a8a73ca28a
- https://git.kernel.org/stable/c/27d6dbdc6485d68075a0ebf8544d6425c1ed84bb
- https://git.kernel.org/stable/c/29a8d4e02fd4840028c38ceb1536cc8f82a257d4
- https://git.kernel.org/stable/c/29ac1d238b3bf126af36037df80d7ecc4822341e
- https://git.kernel.org/stable/c/4e8d6ac8fc9f843e940ab7389db8136634e07989
- https://git.kernel.org/stable/c/688325078a8b5badd6e07ae22b27cd04e9947aec
- https://git.kernel.org/stable/c/96226fbed566f3f686f53a489a29846f2d538080
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43853.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43853
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
