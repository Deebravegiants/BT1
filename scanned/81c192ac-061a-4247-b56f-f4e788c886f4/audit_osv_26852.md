# [H] bpf: Disable preemption in bpf_event_output

## Summary
Severity: High
Advisory: CVE-2023-54173
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54173
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.190, >=5.11.0 <5.15.126, >=5.16.0 <6.1.45, >=6.2.0 <6.4.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Disable preemption in bpf_event_output

We received report [1] of kernel crash, which is caused by
using nesting protection without disabled preemption.

The bpf_event_output can be called by programs executed by
bpf_prog_run_array_cg function that disabled migration but
keeps preemption enabled.

This can cause task to be preempted by another one inside the
nesting protection and lead eventually to two tasks using same
perf_sample_data buffer and cause crashes like:

  BUG: kernel NULL pointer dereference, address: 0000000000000001
  #PF: supervisor instruction fetch in kernel mode
  #PF: error_code(0x0010) - not-present page
  ...
  ? perf_output_sample+0x12a/0x9a0
  ? finish_task_switch.isra.0+0x81/0x280
  ? perf_event_output+0x66/0xa0
  ? bpf_event_output+0x13a/0x190
  ? bpf_event_output_data+0x22/0x40
  ? bpf_prog_dfc84bbde731b257_cil_sock4_connect+0x40a/0xacb
  ? xa_load+0x87/0xe0
  ? __cgroup_bpf_run_filter_sock_addr+0xc1/0x1a0
  ? release_sock+0x3e/0x90
  ? sk_setsockopt+0x1a1/0x12f0
  ? udp_pre_connect+0x36/0x50
  ? inet_dgram_connect+0x93/0xa0
  ? __sys_connect+0xb4/0xe0
  ? udp_setsockopt+0x27/0x40
  ? __pfx_udp_push_pending_frames+0x10/0x10
  ? __sys_setsockopt+0xdf/0x1a0
  ? __x64_sys_connect+0xf/0x20
  ? do_syscall_64+0x3a/0x90
  ? entry_SYSCALL_64_after_hwframe+0x72/0xdc

Fixing this by disabling preemption in bpf_event_output.

[1] https://github.com/cilium/cilium/issues/26756

## References
- https://git.kernel.org/stable/c/063c9ce8e74e07bf94f99cd13146f42867875e8b
- https://git.kernel.org/stable/c/3048cb0dc0cc9dc74ed93690dffef00733bcad5b
- https://git.kernel.org/stable/c/36dd8ca330b76585640ed32255a3c99f901e1502
- https://git.kernel.org/stable/c/c81bdf8f9f2b002d217c3d5357cdea9f2b82ff90
- https://git.kernel.org/stable/c/d62cc390c2e99ae267ffe4b8d7e2e08b6c758c32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54173.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54173
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
