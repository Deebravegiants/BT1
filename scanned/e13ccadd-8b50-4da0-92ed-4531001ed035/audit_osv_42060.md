# [H] mm: shrinker: fix shrinker_info teardown race with expansion

## Summary
Severity: High
Advisory: CVE-2026-64418
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64418
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: shrinker: fix shrinker_info teardown race with expansion

expand_shrinker_info() iterates all visible memcgs under shrinker_mutex,
including memcgs that have not finished ->css_online() yet.

Once pn->shrinker_info has been published, teardown must stay serialized
with expand_shrinker_info() until that memcg is either fully online or no
longer visible to iteration.  Today alloc_shrinker_info() breaks that rule
by dropping shrinker_mutex before freeing a partially initialized
shrinker_info array, which may cause the following race:

CPU0                   CPU1
====                   ====

css_create
--> list_add_tail_rcu(&css->sibling, &parent_css->children);
    online_css
    --> mem_cgroup_css_online
        --> alloc_shrinker_info
            --> alloc node0 info
                rcu_assign_pointer(C->node0->shrinker_info, old0)
                alloc node1 info -> FAIL -> goto err
                mutex_unlock(shrinker_mutex)

                       shrinker_alloc()
                       --> shrinker_memcg_alloc
                           --> mutex_lock(shrinker_mutex)
                               expand_shrinker_info
                               --> mem_cgroup_iter see the memcg
                                   expand_one_shrinker_info
                                   --> old0 = C->node0->shrinker_info
                                       memcpy(new->unit, old0->unit, ...);

                free_shrinker_info
                --> kvfree(old0);

                                       /* double free !! */
                                       kvfree_rcu(old0, rcu);

The same problem exists later in mem_cgroup_css_online().  If
alloc_shrinker_info() succeeds but a subsequent objcg allocation fails,
the free_objcg -> free_shrinker_info() unwind path tears down the already
published pn->shrinker_info arrays without shrinker_mutex.  The
expand_one_shrinker_info() can race with that teardown in the same way,
leading to use-after-free or double-free of the old shrinker_info.

Fix this by serializing shrinker_info teardown with shrinker_mutex, and by
keeping alloc_shrinker_info() error cleanup inside the locked section.

## References
- https://git.kernel.org/stable/c/284c267f013e45d8c89d9fb9373105dc8e6c0947
- https://git.kernel.org/stable/c/6465ff3ce65131c774a312d450abe10f4b9f3875
- https://git.kernel.org/stable/c/65476d31d8056e859c48580f82295ce159196ffe
- https://git.kernel.org/stable/c/b9a280a9a454ed514636351d53fe2a233dc5054b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64418.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64418
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
