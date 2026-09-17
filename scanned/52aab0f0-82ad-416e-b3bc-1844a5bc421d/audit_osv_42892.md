# [H] io_uring/bpf-ops: reject re-registration of an already-bound ops

## Summary
Severity: High
Advisory: CVE-2026-72112
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72112
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/bpf-ops: reject re-registration of an already-bound ops

io_install_bpf() only rejects a second registration on the ctx side
(ctx->bpf_ops) and sets the per-map back-pointer ops->priv
unconditionally. The struct_ops link path never advances a map past
BPF_STRUCT_OPS_STATE_READY, so the same io_uring_bpf_ops map can be
registered more than once, and bpf_io_reg() re-resolves the target ring
via fget(ops->ring_fd) on every call. A caller can therefore point the
same ring_fd at a different io_ring_ctx between two BPF_LINK_CREATE
calls.

The second registration passes the ctx->bpf_ops check (the new ctx has
none) and overwrites ops->priv, orphaning the first ctx. Teardown
(io_eject_bpf()/bpf_io_unreg()) only reaches a ctx through ops->priv, so
the orphaned ctx is never torn down: its ctx->loop_step keeps pointing
into the struct_ops trampoline, which is freed once the map is gone. A
later io_uring_enter() on the orphaned ring then calls the dangling
ctx->loop_step from io_run_loop() -- a use-after-free of freed
executable memory, reachable by a task with CAP_BPF + CAP_PERFMON.

Reject registration when ops->priv is already set, as hid_bpf_reg()
does for its struct_ops.

## References
- https://git.kernel.org/stable/c/0639ea767fe04c288a8d6cb826100fe3d95d4936
- https://git.kernel.org/stable/c/3afc64c61ce906a04f073ca350b46de10e8302f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72112.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72112
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
