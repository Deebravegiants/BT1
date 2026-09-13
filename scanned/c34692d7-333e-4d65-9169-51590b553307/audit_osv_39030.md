# [C] kthread: consolidate kthread exit paths to prevent use-after-free

## Summary
Severity: Critical
Advisory: CVE-2026-43402
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43402
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

kthread: consolidate kthread exit paths to prevent use-after-free

Guillaume reported crashes via corrupted RCU callback function pointers
during KUnit testing. The crash was traced back to the pidfs rhashtable
conversion which replaced the 24-byte rb_node with an 8-byte rhash_head
in struct pid, shrinking it from 160 to 144 bytes.

struct kthread (without CONFIG_BLK_CGROUP) is also 144 bytes. With
CONFIG_SLAB_MERGE_DEFAULT and SLAB_HWCACHE_ALIGN both round up to
192 bytes and share the same slab cache. struct pid.rcu.func and
struct kthread.affinity_node both sit at offset 0x78.

When a kthread exits via make_task_dead() it bypasses kthread_exit() and
misses the affinity_node cleanup. free_kthread_struct() frees the memory
while the node is still linked into the global kthread_affinity_list. A
subsequent list_del() by another kthread writes through dangling list
pointers into the freed and reused memory, corrupting the pid's
rcu.func pointer.

Instead of patching free_kthread_struct() to handle the missed cleanup,
consolidate all kthread exit paths. Turn kthread_exit() into a macro
that calls do_exit() and add kthread_do_exit() which is called from
do_exit() for any task with PF_KTHREAD set. This guarantees that
kthread-specific cleanup always happens regardless of the exit path -
make_task_dead(), direct do_exit(), or kthread_exit().

Replace __to_kthread() with a new tsk_is_kthread() accessor in the
public header. Export do_exit() since module code using the
kthread_exit() macro now needs it directly.

## References
- https://git.kernel.org/stable/c/28aaa9c39945b7925a1cc1d513c8f21ed38f5e4f
- https://git.kernel.org/stable/c/4729c7b00a347fd37d0cbc265b85f2884c3e06b6
- https://git.kernel.org/stable/c/5a591d7a5e48d30100943940a30a6ab41b15c672
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43402.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43402
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
