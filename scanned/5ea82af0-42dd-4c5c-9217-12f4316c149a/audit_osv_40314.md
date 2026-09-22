# [H] net: qrtr: fix refcount saturation and potential UAF in qrtr_port_remove

## Summary
Severity: High
Advisory: CVE-2026-52947
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52947
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qrtr: fix refcount saturation and potential UAF in qrtr_port_remove

In qrtr_port_remove(), the socket reference count is decremented via
__sock_put() before the port is removed from the qrtr_ports XArray and
before the RCU grace period elapses.

This breaks the fundamental RCU update paradigm. It exposes a race
window where a concurrent RCU reader (such as qrtr_reset_ports() or
qrtr_port_lookup()) can obtain a pointer to the socket from the XArray,
and attempt to call sock_hold() on a socket whose reference count has
already dropped to zero.

This exact race condition was hit during syzkaller fuzzing, leading to
the following refcount saturation warning and a potential Use-After-Free:

  refcount_t: saturated; leaking memory.
  WARNING: CPU: 3 PID: 1273 at lib/refcount.c:22 refcount_warn_saturate+0xae/0x1d0
  Modules linked in: qrtr(+) bochs drm_shmem_helper ...
  Call Trace:
   <TASK>
   qrtr_reset_ports net/qrtr/af_qrtr.c:768 [inline] [qrtr]
   __qrtr_bind.isra.0+0x48b/0x570 net/qrtr/af_qrtr.c:805 [qrtr]
   qrtr_bind+0x17d/0x210 net/qrtr/af_qrtr.c:901 [qrtr]
   kernel_bind+0xe4/0x120 net/socket.c:3592
   qrtr_ns_init+0x1a6/0x380 net/qrtr/ns.c:715 [qrtr]
   qrtr_proto_init+0x3b/0xff0 net/qrtr/af_qrtr.c:169 [qrtr]
   do_one_initcall+0xf5/0x5e0 init/main.c:1283
   ...
   </TASK>

Fix this by deferring the reference count decrement until after the
xa_erase() and the synchronize_rcu() complete.

(Note: The v1 of this patch incorrectly replaced __sock_put() with
sock_put(). As Simon Horman pointed out, the callers of qrtr_port_remove()
still hold a reference to the socket, so freeing the socket memory here
would lead to a subsequent UAF in the caller. Thus, the __sock_put() is
kept, but only repositioned to close the RCU race.)

## References
- https://git.kernel.org/stable/c/03bfa95e452e2b6ccd76a332060ae4feaf5ad84d
- https://git.kernel.org/stable/c/2047c2aa0963bb2872fd722300a15bcb441a4c00
- https://git.kernel.org/stable/c/2aa4c12723fe432e623462a3be42a197a128722b
- https://git.kernel.org/stable/c/3b20ec8f31e8a6a6782243f473b0abd3463621df
- https://git.kernel.org/stable/c/474293d90880622fde9d2430fb0165767090f7b3
- https://git.kernel.org/stable/c/7de2d447072be3b1a76793f034432338fc9c494b
- https://git.kernel.org/stable/c/a2171131ecda1ed61a594a1eb715e75fdad0fef5
- https://git.kernel.org/stable/c/ab269990ed58143a92a263be1bee626d82ac03da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52947.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52947
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
