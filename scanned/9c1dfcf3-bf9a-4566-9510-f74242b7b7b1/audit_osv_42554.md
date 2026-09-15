# [H] xfrm: clear mode callbacks after failed mode setup

## Summary
Severity: High
Advisory: CVE-2026-68415
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68415
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: clear mode callbacks after failed mode setup

xfrm_state_gc_task can run long after a failed IPTFS state setup. In the
reproduced case, __xfrm_init_state() cached x->mode_cbs, IPTFS setup
returned -ENOMEM before publishing mode_data, and the temporary module
reference from xfrm_get_mode_cbs() was dropped immediately. The dead state
then kept x->mode_cbs until deferred GC ran after xfrm_iptfs had been
unloaded.

Clear x->mode_cbs when mode init or clone fails before publishing
mode_data. Those states never installed mode-specific state or the
long-term IPTFS module pin, so deferred GC has nothing mode-specific to
destroy and must not retain a callback table pointer past the temporary
lookup reference.

The buggy scenario involves two paths, with each column showing the order
within that path:

failed setup path:
1. cache x->mode_cbs
2. mode setup fails before mode_data
3. drop the temporary module ref
4. dead state keeps x->mode_cbs cached

GC/unload path:
1. xfrm_state_put() queues GC work
2. xfrm_iptfs unloads later
3. xfrm_state_gc_task runs
4. GC dereferences stale x->mode_cbs

This also covers the failed clone path where clone_state() returns before
publishing mode_data.

Validation reproduced this kernel report:
Kernel panic - not syncing: Fatal exception
CONFIG_FAULT_INJECTION_STACKTRACE_FILTER=y
failslab_stacktrace_filter matched xfrm_iptfs frames
ack_error=-12
FAULT_INJECTION: forcing a failure
BUG: unable to handle page fault
Workqueue: events xfrm_state_gc_task
RIP: xfrm_state_gc_task+0x142/0x650
Modules linked in: esp4_offload xfrm_user [last unloaded: xfrm_iptfs]
Kernel panic - not syncing: Fatal exception

## References
- https://git.kernel.org/stable/c/2538bd3cd1ff5af655908469544ac7b7ae259386
- https://git.kernel.org/stable/c/9845a35986a658816f7752f7ebd7c455a4c7dfdf
- https://git.kernel.org/stable/c/c37a079230128a5237f45fb4e181bc069a5c2955
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68415.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68415
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
