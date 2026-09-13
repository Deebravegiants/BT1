# [H] mptcp: prevent BPF accessing lowat from a subflow socket.

## Summary
Severity: High
Advisory: CVE-2024-35894
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35894
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: prevent BPF accessing lowat from a subflow socket.

Alexei reported the following splat:

 WARNING: CPU: 32 PID: 3276 at net/mptcp/subflow.c:1430 subflow_data_ready+0x147/0x1c0
 Modules linked in: dummy bpf_testmod(O) [last unloaded: bpf_test_no_cfi(O)]
 CPU: 32 PID: 3276 Comm: test_progs Tainted: GO       6.8.0-12873-g2c43c33bfd23
 Call Trace:
  <TASK>
  mptcp_set_rcvlowat+0x79/0x1d0
  sk_setsockopt+0x6c0/0x1540
  __bpf_setsockopt+0x6f/0x90
  bpf_sock_ops_setsockopt+0x3c/0x90
  bpf_prog_509ce5db2c7f9981_bpf_test_sockopt_int+0xb4/0x11b
  bpf_prog_dce07e362d941d2b_bpf_test_socket_sockopt+0x12b/0x132
  bpf_prog_348c9b5faaf10092_skops_sockopt+0x954/0xe86
  __cgroup_bpf_run_filter_sock_ops+0xbc/0x250
  tcp_connect+0x879/0x1160
  tcp_v6_connect+0x50c/0x870
  mptcp_connect+0x129/0x280
  __inet_stream_connect+0xce/0x370
  inet_stream_connect+0x36/0x50
  bpf_trampoline_6442491565+0x49/0xef
  inet_stream_connect+0x5/0x50
  __sys_connect+0x63/0x90
  __x64_sys_connect+0x14/0x20

The root cause of the issue is that bpf allows accessing mptcp-level
proto_ops from a tcp subflow scope.

Fix the issue detecting the problematic call and preventing any action.

## References
- https://git.kernel.org/stable/c/3ffb1ab698376f09cc33101c07c1be229389fe29
- https://git.kernel.org/stable/c/ee3c845787b621cfe82c2e52c513024a9d7a78f5
- https://git.kernel.org/stable/c/fcf4692fa39e86a590c14a4af2de704e1d20a3b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35894.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35894
- https://security.netapp.com/advisory/ntap-20250321-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
