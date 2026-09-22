# [H] net/mlx5e: Fix HV VHCA stats agent registration race

## Summary
Severity: High
Advisory: CVE-2026-72342
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72342
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Fix HV VHCA stats agent registration race

mlx5e_hv_vhca_stats_create() registers the stats agent through
mlx5_hv_vhca_agent_create(). The helper publishes the agent in
hv_vhca->agents[type] under agents_lock and immediately schedules an
asynchronous control invalidation on the HV VHCA workqueue before
returning to mlx5e.

The asynchronous invalidation invokes the control agent's invalidate
callback, which reads the hypervisor control block and forwards the
command to mlx5e_hv_vhca_stats_control(). That callback may either:

  - call cancel_delayed_work_sync(&priv->stats_agent.work), or
  - call queue_delayed_work(priv->wq, &sagent->work, sagent->delay).

However, the delayed_work and priv->stats_agent.agent are only
initialized after mlx5_hv_vhca_agent_create() returns to mlx5e:

    agent = mlx5_hv_vhca_agent_create(...);   /* publish + invalidate */
    ...
    priv->stats_agent.agent = agent;          /* too late */
    INIT_DELAYED_WORK(&priv->stats_agent.work, ...); /* too late */

If the asynchronous control path runs before the two assignments
above, it can:

  - Operate on an uninitialized delayed_work whose timer.function is
    NULL. queue_delayed_work() calls add_timer() unconditionally, so
    when the timer expires the timer softirq invokes a NULL function
    pointer.
  - Re-initialize the timer later through INIT_DELAYED_WORK() while
    the timer is already enqueued in the timer wheel, corrupting the
    hlist (entry.pprev cleared while the previous bucket node still
    points at this entry).
  - When the worker eventually runs, mlx5e_hv_vhca_stats_work() reads
    sagent->agent (NULL) and dereferences it inside
    mlx5_hv_vhca_agent_write().

Fix this by:

  - Initializing priv->stats_agent.work before invoking
    mlx5_hv_vhca_agent_create(), so the work is always in a valid
    state when the control callback observes it.
  - Adding a struct mlx5_hv_vhca_agent **ctx_update out-parameter
    to mlx5_hv_vhca_agent_create(). The helper writes the agent
    pointer to *ctx_update before publishing into hv_vhca->agents[]
    and triggering the agents_update flow, so any callback
    subsequently invoked from that flow already sees a valid
    priv->stats_agent.agent. This avoids having the control
    callback participate in agent initialization.

While at it, access priv->stats_agent.agent with
READ_ONCE()/WRITE_ONCE() for the cross-CPU access with the worker, and
clear priv->stats_agent.buf on the agent_create() failure path.

## References
- https://git.kernel.org/stable/c/24c77044cdfcf5b8b2e9f3b620d8b9aa392d9add
- https://git.kernel.org/stable/c/60fddda7207d81fea71463abd403f0b10f74f2e1
- https://git.kernel.org/stable/c/89b25b5f46f488ea3b29b3444864c76944c9075b
- https://git.kernel.org/stable/c/b0fd6d3bb06182f19f3b59a53f57b5098b99048a
- https://git.kernel.org/stable/c/e8fc3304cb67fb1d7d11ff9ef9abd5fb64e7e1d5
- https://git.kernel.org/stable/c/f5677797b094c3ec5fb350eb8ea7710b88a3d018
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72342.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72342
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
