# [H] CVE-2021-47318

## Summary
Severity: High
Advisory: CVE-2021-47318
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47318
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

arch_topology: Avoid use-after-free for scale_freq_data

Currently topology_scale_freq_tick() (which gets called from
scheduler_tick()) may end up using a pointer to "struct
scale_freq_data", which was previously cleared by
topology_clear_scale_freq_source(), as there is no protection in place
here. The users of topology_clear_scale_freq_source() though needs a
guarantee that the previously cleared scale_freq_data isn't used
anymore, so they can free the related resources.

Since topology_scale_freq_tick() is called from scheduler tick, we don't
want to add locking in there. Use the RCU update mechanism instead
(which is already used by the scheduler's utilization update path) to
guarantee race free updates here.

synchronize_rcu() makes sure that all RCU critical sections that started
before it is called, will finish before it returns. And so the callers
of topology_clear_scale_freq_source() don't need to worry about their
callback getting called anymore.

## References
- https://git.kernel.org/stable/c/83150f5d05f065fb5c12c612f119015cabdcc124
- https://git.kernel.org/stable/c/ccdf7e073170886bc370c613e269de610a794c4a
