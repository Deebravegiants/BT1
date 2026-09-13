# [C] nvmet-tcp: propagate nvmet_tcp_build_pdu_iovec() errors to its callers

## Summary
Severity: Critical
Advisory: CVE-2026-52989
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52989
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: propagate nvmet_tcp_build_pdu_iovec() errors to its callers

Currently, when nvmet_tcp_build_pdu_iovec() detects an out-of-bounds
PDU length or offset, it triggers nvmet_tcp_fatal_error(cmd->queue)
and returns early. However, because the function returns void, the
callers are entirely unaware that a fatal error has occurred and
that the cmd->recv_msg.msg_iter was left uninitialized.

Callers such as nvmet_tcp_handle_h2c_data_pdu() proceed to blindly
overwrite the queue state with queue->rcv_state = NVMET_TCP_RECV_DATA
Consequently, the socket receiving loop may attempt to read incoming
network data into the uninitialized iterator.

Fix this by shifting the error handling responsibility to the callers.

## References
- https://git.kernel.org/stable/c/046fa5c72d15cd8e2d592e275697ea399d8f76b0
- https://git.kernel.org/stable/c/3df42a854686fa06484e37ac1a3931c8e3e3453c
- https://git.kernel.org/stable/c/c2a11441538bdbbc5aa003f190995eba93a89b88
- https://git.kernel.org/stable/c/d7c8f95f599b3b38a717d2e771c3f8c174f657c3
- https://git.kernel.org/stable/c/ea8e356acb165cb1fd75537a52e1f66e5e76c538
- https://git.kernel.org/stable/c/f9204a2b78dd18374d3bcf9bf93d9021ce22de1b
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52989.json
- https://access.redhat.com/security/cve/CVE-2026-52989
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52989.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52989
- https://bugzilla.redhat.com/show_bug.cgi?id=2492443
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
