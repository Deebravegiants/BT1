# [H] bpf: Add sk_is_inet and IS_ICSK check in tls_sw_has_ctx_tx/rx

## Summary
Severity: High
Advisory: CVE-2024-53091
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/CVE-2024-53091
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.62, >=6.7.0 <6.11.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Add sk_is_inet and IS_ICSK check in tls_sw_has_ctx_tx/rx

As the introduction of the support for vsock and unix sockets in sockmap,
tls_sw_has_ctx_tx/rx cannot presume the socket passed in must be IS_ICSK.
vsock and af_unix sockets have vsock_sock and unix_sock instead of
inet_connection_sock. For these sockets, tls_get_ctx may return an invalid
pointer and cause page fault in function tls_sw_ctx_rx.

BUG: unable to handle page fault for address: 0000000000040030
Workqueue: vsock-loopback vsock_loopback_work
RIP: 0010:sk_psock_strp_data_ready+0x23/0x60
Call Trace:
 ? __die+0x81/0xc3
 ? no_context+0x194/0x350
 ? do_page_fault+0x30/0x110
 ? async_page_fault+0x3e/0x50
 ? sk_psock_strp_data_ready+0x23/0x60
 virtio_transport_recv_pkt+0x750/0x800
 ? update_load_avg+0x7e/0x620
 vsock_loopback_work+0xd0/0x100
 process_one_work+0x1a7/0x360
 worker_thread+0x30/0x390
 ? create_worker+0x1a0/0x1a0
 kthread+0x112/0x130
 ? __kthread_cancel_work+0x40/0x40
 ret_from_fork+0x1f/0x40

v2:
  - Add IS_ICSK check
v3:
  - Update the commits in Fixes

## References
- https://git.kernel.org/stable/c/44d0469f79bd3d0b3433732877358df7dc6b17b1
- https://git.kernel.org/stable/c/6781cfa93a6a1b7f5be6819a5a2dd8f30f47ca26
- https://git.kernel.org/stable/c/a078a480ff3f43d74d8a024ae10c3c7daf6db149
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53091.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53091
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
