# [C] veth: reduce XDP no_direct return section to fix race

## Summary
Severity: Critical
Advisory: CVE-2025-68341
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-68341
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.61, >=6.13.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

veth: reduce XDP no_direct return section to fix race

As explain in commit fa349e396e48 ("veth: Fix race with AF_XDP exposing
old or uninitialized descriptors") for veth there is a chance after
napi_complete_done() that another CPU can manage start another NAPI
instance running veth_pool(). For NAPI this is correctly handled as the
napi_schedule_prep() check will prevent multiple instances from getting
scheduled, but for the remaining code in veth_pool() this can run
concurrent with the newly started NAPI instance.

The problem/race is that xdp_clear_return_frame_no_direct() isn't
designed to be nested.

Prior to commit 401cb7dae813 ("net: Reference bpf_redirect_info via
task_struct on PREEMPT_RT.") the temporary BPF net context
bpf_redirect_info was stored per CPU, where this wasn't an issue. Since
this commit the BPF context is stored in 'current' task_struct. When
running veth in threaded-NAPI mode, then the kthread becomes the storage
area. Now a race exists between two concurrent veth_pool() function calls
one exiting NAPI and one running new NAPI, both using the same BPF net
context.

Race is when another CPU gets within the xdp_set_return_frame_no_direct()
section before exiting veth_pool() calls the clear-function
xdp_clear_return_frame_no_direct().

## References
- https://git.kernel.org/stable/c/a14602fcae17a3f1cb8a8521bedf31728f9e7e39
- https://git.kernel.org/stable/c/c1ceabcb347d1b0f7e70a7384ec7eff3847b7628
- https://git.kernel.org/stable/c/d0bd018ad72a8a598ae709588934135017f8af52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68341.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68341
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
