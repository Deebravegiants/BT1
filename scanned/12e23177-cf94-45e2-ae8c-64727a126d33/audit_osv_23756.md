# [M] rxrpc: Fix listen() setting the bar too high for the prealloc rings

## Summary
Severity: Medium
Advisory: CVE-2022-49450
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49450
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix listen() setting the bar too high for the prealloc rings

AF_RXRPC's listen() handler lets you set the backlog up to 32 (if you bump
up the sysctl), but whilst the preallocation circular buffers have 32 slots
in them, one of them has to be a dead slot because we're using CIRC_CNT().

This means that listen(rxrpc_sock, 32) will cause an oops when the socket
is closed because rxrpc_service_prealloc_one() allocated one too many calls
and rxrpc_discard_prealloc() won't then be able to get rid of them because
it'll think the ring is empty.  rxrpc_release_calls_on_socket() then tries
to abort them, but oopses because call->peer isn't yet set.

Fix this by setting the maximum backlog to RXRPC_BACKLOG_MAX - 1 to match
the ring capacity.

 BUG: kernel NULL pointer dereference, address: 0000000000000086
 ...
 RIP: 0010:rxrpc_send_abort_packet+0x73/0x240 [rxrpc]
 Call Trace:
  <TASK>
  ? __wake_up_common_lock+0x7a/0x90
  ? rxrpc_notify_socket+0x8e/0x140 [rxrpc]
  ? rxrpc_abort_call+0x4c/0x60 [rxrpc]
  rxrpc_release_calls_on_socket+0x107/0x1a0 [rxrpc]
  rxrpc_release+0xc9/0x1c0 [rxrpc]
  __sock_release+0x37/0xa0
  sock_close+0x11/0x20
  __fput+0x89/0x240
  task_work_run+0x59/0x90
  do_exit+0x319/0xaa0

## References
- https://git.kernel.org/stable/c/369de57492c4f1a42563c5a3bd365822ca3bfc79
- https://git.kernel.org/stable/c/4a3a78b7918bdd723d8c7c9786522ca969bffcc4
- https://git.kernel.org/stable/c/5b4826657d36c218e9f08e8d3223b0edce3de88f
- https://git.kernel.org/stable/c/616f76498d5ddf26b997caf64a95cda3c8a55533
- https://git.kernel.org/stable/c/61fb38cfbb1d54d3dafd0c25752f684b3cd00b32
- https://git.kernel.org/stable/c/88e22159750b0d55793302eeed8ee603f5c1a95c
- https://git.kernel.org/stable/c/91b34bf0409f43bb60453bab23c5beadd726d022
- https://git.kernel.org/stable/c/b3a9b227d5e7467b8518160ff034ea22bb9de573
- https://git.kernel.org/stable/c/e198f1930050e3115c80b67d9249f80f98a27c67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49450.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49450
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
