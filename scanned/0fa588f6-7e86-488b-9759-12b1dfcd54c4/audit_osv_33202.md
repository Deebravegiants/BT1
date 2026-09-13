# [M] bpf: Tell memcg to use allow_spinning=false path in bpf_timer_init()

## Summary
Severity: Medium
Advisory: CVE-2025-39886
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39886
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.107, >=6.7.0 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Tell memcg to use allow_spinning=false path in bpf_timer_init()

Currently, calling bpf_map_kmalloc_node() from __bpf_async_init() can
cause various locking issues; see the following stack trace (edited for
style) as one example:

...
 [10.011566]  do_raw_spin_lock.cold
 [10.011570]  try_to_wake_up             (5) double-acquiring the same
 [10.011575]  kick_pool                      rq_lock, causing a hardlockup
 [10.011579]  __queue_work
 [10.011582]  queue_work_on
 [10.011585]  kernfs_notify
 [10.011589]  cgroup_file_notify
 [10.011593]  try_charge_memcg           (4) memcg accounting raises an
 [10.011597]  obj_cgroup_charge_pages        MEMCG_MAX event
 [10.011599]  obj_cgroup_charge_account
 [10.011600]  __memcg_slab_post_alloc_hook
 [10.011603]  __kmalloc_node_noprof
...
 [10.011611]  bpf_map_kmalloc_node
 [10.011612]  __bpf_async_init
 [10.011615]  bpf_timer_init             (3) BPF calls bpf_timer_init()
 [10.011617]  bpf_prog_xxxxxxxxxxxxxxxx_fcg_runnable
 [10.011619]  bpf__sched_ext_ops_runnable
 [10.011620]  enqueue_task_scx           (2) BPF runs with rq_lock held
 [10.011622]  enqueue_task
 [10.011626]  ttwu_do_activate
 [10.011629]  sched_ttwu_pending         (1) grabs rq_lock
...

The above was reproduced on bpf-next (b338cf849ec8) by modifying
./tools/sched_ext/scx_flatcg.bpf.c to call bpf_timer_init() during
ops.runnable(), and hacking the memcg accounting code a bit to make
a bpf_timer_init() call more likely to raise an MEMCG_MAX event.

We have also run into other similar variants (both internally and on
bpf-next), including double-acquiring cgroup_file_kn_lock, the same
worker_pool::lock, etc.

As suggested by Shakeel, fix this by using __GFP_HIGH instead of
GFP_ATOMIC in __bpf_async_init(), so that e.g. if try_charge_memcg()
raises an MEMCG_MAX event, we call __memcg_memory_event() with
@allow_spinning=false and avoid calling cgroup_file_notify() there.

Depends on mm patch
"memcg: skip cgroup_file_notify if spinning is not allowed":
https://lore.kernel.org/bpf/20250905201606.66198-1-shakeel.butt@linux.dev/

v0 approach s/bpf_map_kmalloc_node/bpf_mem_alloc/
https://lore.kernel.org/bpf/20250905061919.439648-1-yepeilin@google.com/
v1 approach:
https://lore.kernel.org/bpf/20250905234547.862249-1-yepeilin@google.com/

## References
- https://git.kernel.org/stable/c/449682e76f32601f211816d3e2100bed87e67a4c
- https://git.kernel.org/stable/c/6d78b4473cdb08b74662355a9e8510bde09c511e
- https://git.kernel.org/stable/c/ac70cd446f83ccb25532b343919ab86eacdcd06a
- https://git.kernel.org/stable/c/cd1fd26bb13473c1734e3026b2b97025a0a4087b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39886.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39886
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
