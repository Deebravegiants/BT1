# [H] xfrm: Fix work re-schedule after cancel in xfrm_nat_keepalive_net_fini()

## Summary
Severity: High
Advisory: CVE-2026-31406
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-31406
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: Fix work re-schedule after cancel in xfrm_nat_keepalive_net_fini()

After cancel_delayed_work_sync() is called from
xfrm_nat_keepalive_net_fini(), xfrm_state_fini() flushes remaining
states via __xfrm_state_delete(), which calls
xfrm_nat_keepalive_state_updated() to re-schedule nat_keepalive_work.

The following is a simple race scenario:

           cpu0                             cpu1

cleanup_net() [Round 1]
  ops_undo_list()
    xfrm_net_exit()
      xfrm_nat_keepalive_net_fini()
        cancel_delayed_work_sync(nat_keepalive_work);
      xfrm_state_fini()
        xfrm_state_flush()
          xfrm_state_delete(x)
            __xfrm_state_delete(x)
              xfrm_nat_keepalive_state_updated(x)
                schedule_delayed_work(nat_keepalive_work);
  rcu_barrier();
  net_complete_free();
  net_passive_dec(net);
    llist_add(&net->defer_free_list, &defer_free_list);

cleanup_net() [Round 2]
  rcu_barrier();
  net_complete_free()
    kmem_cache_free(net_cachep, net);
                                     nat_keepalive_work()
                                       // on freed net

To prevent this, cancel_delayed_work_sync() is replaced with
disable_delayed_work_sync().

## References
- https://git.kernel.org/stable/c/21f2fc49ca6faa393c31da33b8a4e6c41fc84c13
- https://git.kernel.org/stable/c/2255ed6adbc3100d2c4a83abd9d0396d04b87792
- https://git.kernel.org/stable/c/32d0f44c2f14d60fe8e920e69a28c11051543ec1
- https://git.kernel.org/stable/c/daf8e3b253aa760ff9e96c7768a464bc1d6b3c90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31406.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31406
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
