# [H] xfrm: iptfs: reset runtime state when cloning SAs

## Summary
Severity: High
Advisory: CVE-2026-63911
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63911
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: iptfs: reset runtime state when cloning SAs

iptfs_clone_state() clones the IPTFS mode data with kmemdup(). This
copies runtime objects which must not be shared with the original SA,
including the embedded sk_buff_head, hrtimers, spinlock, and in-flight
reassembly/reorder state.

If xfrm_state_migrate() fails after clone_state() but before the later
init_state() call has reinitialized those fields, the cloned state can be
destroyed by xfrm_state_gc_task() with list and timer state copied from the
original SA. With queued packets this lets the clone splice and free skbs
owned by the original IPTFS queue, leading to use-after-free and
double-free reports in iptfs_destroy_state() and skb release paths.

Reinitialize the clone's runtime state before publishing it through
x->mode_data. Because clone_state() now publishes a destroyable mode_data
object before init_state(), take the mode callback module reference there.
Avoid taking it again from __iptfs_init_state() for the same object.

## References
- https://git.kernel.org/stable/c/7f83d174073234839aea176f265e517e0d50a1d2
- https://git.kernel.org/stable/c/9327252e04626d4bb02ca8c0c108fbe8eabf0c5a
- https://git.kernel.org/stable/c/dfb9f6cbfa9826655a49698cf90eb800fce2178e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63911.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63911
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
