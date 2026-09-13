# [M] rcu: Protect rcu_print_task_exp_stall() ->exp_tasks access

## Summary
Severity: Medium
Advisory: CVE-2023-53419
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53419
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rcu: Protect rcu_print_task_exp_stall() ->exp_tasks access

For kernels built with CONFIG_PREEMPT_RCU=y, the following scenario can
result in a NULL-pointer dereference:

           CPU1                                           CPU2
rcu_preempt_deferred_qs_irqrestore                rcu_print_task_exp_stall
  if (special.b.blocked)                            READ_ONCE(rnp->exp_tasks) != NULL
    raw_spin_lock_rcu_node
    np = rcu_next_node_entry(t, rnp)
    if (&t->rcu_node_entry == rnp->exp_tasks)
      WRITE_ONCE(rnp->exp_tasks, np)
      ....
      raw_spin_unlock_irqrestore_rcu_node
                                                    raw_spin_lock_irqsave_rcu_node
                                                    t = list_entry(rnp->exp_tasks->prev,
                                                        struct task_struct, rcu_node_entry)
                                                    (if rnp->exp_tasks is NULL, this
                                                       will dereference a NULL pointer)

The problem is that CPU2 accesses the rcu_node structure's->exp_tasks
field without holding the rcu_node structure's ->lock and CPU2 did
not observe CPU1's change to rcu_node structure's ->exp_tasks in time.
Therefore, if CPU1 sets rcu_node structure's->exp_tasks pointer to NULL,
then CPU2 might dereference that NULL pointer.

This commit therefore holds the rcu_node structure's ->lock while
accessing that structure's->exp_tasks field.

[ paulmck: Apply Frederic Weisbecker feedback. ]

## References
- https://git.kernel.org/stable/c/2bc0ae94ef1f9ed322d8ee439de3239ea3632ab2
- https://git.kernel.org/stable/c/3c1566bca3f8349f12b75d0a2d5e4a20ad6262ec
- https://git.kernel.org/stable/c/a7d21b8585894e6fff973f6ddae42f02b13f600f
- https://git.kernel.org/stable/c/d0a8c0e31a09ec1efd53079083e2a677956b4d91
- https://git.kernel.org/stable/c/e30a55e98ae6c44253d8b129efefd5da5bc6e3bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53419.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53419
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
