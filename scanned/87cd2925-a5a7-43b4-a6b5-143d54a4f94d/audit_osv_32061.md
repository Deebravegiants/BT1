# [H] mptcp: fix NULL pointer in can_accept_new_subflow

## Summary
Severity: High
Advisory: CVE-2025-23145
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-23145
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix NULL pointer in can_accept_new_subflow

When testing valkey benchmark tool with MPTCP, the kernel panics in
'mptcp_can_accept_new_subflow' because subflow_req->msk is NULL.

Call trace:

  mptcp_can_accept_new_subflow (./net/mptcp/subflow.c:63 (discriminator 4)) (P)
  subflow_syn_recv_sock (./net/mptcp/subflow.c:854)
  tcp_check_req (./net/ipv4/tcp_minisocks.c:863)
  tcp_v4_rcv (./net/ipv4/tcp_ipv4.c:2268)
  ip_protocol_deliver_rcu (./net/ipv4/ip_input.c:207)
  ip_local_deliver_finish (./net/ipv4/ip_input.c:234)
  ip_local_deliver (./net/ipv4/ip_input.c:254)
  ip_rcv_finish (./net/ipv4/ip_input.c:449)
  ...

According to the debug log, the same req received two SYN-ACK in a very
short time, very likely because the client retransmits the syn ack due
to multiple reasons.

Even if the packets are transmitted with a relevant time interval, they
can be processed by the server on different CPUs concurrently). The
'subflow_req->msk' ownership is transferred to the subflow the first,
and there will be a risk of a null pointer dereference here.

This patch fixes this issue by moving the 'subflow_req->msk' under the
`own_req == true` conditional.

Note that the !msk check in subflow_hmac_valid() can be dropped, because
the same check already exists under the own_req mpj branch where the
code has been moved to.

## References
- https://git.kernel.org/stable/c/443041deb5ef6a1289a99ed95015ec7442f141dc
- https://git.kernel.org/stable/c/4b2649b9717678aeb097893cc49f59311a1ecab0
- https://git.kernel.org/stable/c/7f9ae060ed64aef8f174c5f1ea513825b1be9af1
- https://git.kernel.org/stable/c/855bf0aacd51fced11ea9aa0d5101ee0febaeadb
- https://git.kernel.org/stable/c/8cf7fef1bb2ffea7792bcbf71ca00216cecc725d
- https://git.kernel.org/stable/c/b3088bd2a6790c8efff139d86d7a9d0b1305977b
- https://git.kernel.org/stable/c/dc81e41a307df523072186b241fa8244fecd7803
- https://git.kernel.org/stable/c/efd58a8dd9e7a709a90ee486a4247c923d27296f
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23145.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23145
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
