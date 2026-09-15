# [H] net/sched: act_ct: Only release RCU read lock after ct_ft

## Summary
Severity: High
Advisory: CVE-2026-46319
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46319
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_ct: Only release RCU read lock after ct_ft

When looking up a flow table in act_ct in tcf_ct_flow_table_get(),
rhashtable_lookup_fast() internally opens and closes an RCU read critical
section before returning ct_ft.
The tcf_ct_flow_table_cleanup_work() can complete before refcount_inc_not_zero()
is invoked on the returned ct_ft resulting in a UAF on the already freed ct_ft
object. This vulnerability can lead to privilege escalation.

Analysis from zdi-disclosures@trendmicro.com:
When initializing act_ct, tcf_ct_init() is called, which internally triggers
tcf_ct_flow_table_get().

static int tcf_ct_flow_table_get(struct net *net, struct tcf_ct_params *params)

{
                struct zones_ht_key key = { .net = net, .zone = params->zone };
                struct tcf_ct_flow_table *ct_ft;
                int err = -ENOMEM;

                mutex_lock(&zones_mutex);
                ct_ft = rhashtable_lookup_fast(&zones_ht, &key, zones_params); // [1]
                if (ct_ft && refcount_inc_not_zero(&ct_ft->ref)) // [2]
                                goto out_unlock;
                ...
}

static __always_inline void *rhashtable_lookup_fast(
                struct rhashtable *ht, const void *key,
                const struct rhashtable_params params)
{
                void *obj;

                rcu_read_lock();
                obj = rhashtable_lookup(ht, key, params);
                rcu_read_unlock();

                return obj;
}

At [1], rhashtable_lookup_fast() looks up and returns the corresponding ct_ft
from zones_ht . The lookup is performed within an RCU read critical section
through rcu_read_lock() / rcu_read_unlock(), which prevents the object from
being freed. However, at the point of function return, rcu_read_unlock() has
already been called, and there is nothing preventing ct_ft from being freed
before reaching refcount_inc_not_zero(&ct_ft->ref) at [2]. This interval becomes
the race window, during which ct_ft can be freed.

Free Process:

tcf_ct_flow_table_put() is executed through the path tcf_ct_cleanup() call_rcu()
tcf_ct_params_free_rcu() tcf_ct_params_free() tcf_ct_flow_table_put().

static void tcf_ct_flow_table_put(struct tcf_ct_flow_table *ct_ft)
{
                if (refcount_dec_and_test(&ct_ft->ref)) {
                                rhashtable_remove_fast(&zones_ht, &ct_ft->node, zones_params);
                                INIT_RCU_WORK(&ct_ft->rwork, tcf_ct_flow_table_cleanup_work); // [3]
                                queue_rcu_work(act_ct_wq, &ct_ft->rwork);
                }
}

At [3], tcf_ct_flow_table_cleanup_work() is scheduled as RCU work

static void tcf_ct_flow_table_cleanup_work(struct work_struct *work)

{
                struct tcf_ct_flow_table *ct_ft;
                struct flow_block *block;

                ct_ft = container_of(to_rcu_work(work), struct tcf_ct_flow_table,
                                                                rwork);
                nf_flow_table_free(&ct_ft->nf_ft);
                block = &ct_ft->nf_ft.flow_block;
                down_write(&ct_ft->nf_ft.flow_block_lock);
                WARN_ON(!list_empty(&block->cb_list));
                up_write(&ct_ft->nf_ft.flow_block_lock);
                kfree(ct_ft); // [4]

                module_put(THIS_MODULE);
}

tcf_ct_flow_table_cleanup_work() frees ct_ft at [4]. When this function executes
between [1] and [2], UAF occurs.

This race condition has a very short race window, making it generally
difficult to trigger. Therefore, to trigger the vulnerability an msleep(100) was
inserted after[1]

## References
- https://git.kernel.org/stable/c/17dfb67cb399b660105d9a8c6100851c0d0cdc70
- https://git.kernel.org/stable/c/3e20e1b3058e0b94638e7b931c138e840e266724
- https://git.kernel.org/stable/c/4c727c6967a41b37efe0f26332ca9ec5b74785a3
- https://git.kernel.org/stable/c/67c9ecc9f2575273ed1323e312881fc98ac83d6d
- https://git.kernel.org/stable/c/a2e0c045c87aa252eb61412e67dd91f2c2b19f81
- https://git.kernel.org/stable/c/ece578ca61e572df96cfc80456357ebfae0b4b9e
- https://git.kernel.org/stable/c/f23424a0ddadb494d4bd57056a7ca703312d3a7b
- https://git.kernel.org/stable/c/f462dca0c8415bf0058d0ffa476354c4476d0f09
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46319.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46319
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
