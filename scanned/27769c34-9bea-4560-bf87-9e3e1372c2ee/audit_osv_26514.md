# [M] sctp: check send stream number after wait_for_sndbuf

## Summary
Severity: Medium
Advisory: CVE-2023-53296
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53296
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.281, >=4.20.0 <5.4.241, >=5.5.0 <5.10.178, >=5.11.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: check send stream number after wait_for_sndbuf

This patch fixes a corner case where the asoc out stream count may change
after wait_for_sndbuf.

When the main thread in the client starts a connection, if its out stream
count is set to N while the in stream count in the server is set to N - 2,
another thread in the client keeps sending the msgs with stream number
N - 1, and waits for sndbuf before processing INIT_ACK.

However, after processing INIT_ACK, the out stream count in the client is
shrunk to N - 2, the same to the in stream count in the server. The crash
occurs when the thread waiting for sndbuf is awake and sends the msg in a
non-existing stream(N - 1), the call trace is as below:

  KASAN: null-ptr-deref in range [0x0000000000000038-0x000000000000003f]
  Call Trace:
   <TASK>
   sctp_cmd_send_msg net/sctp/sm_sideeffect.c:1114 [inline]
   sctp_cmd_interpreter net/sctp/sm_sideeffect.c:1777 [inline]
   sctp_side_effects net/sctp/sm_sideeffect.c:1199 [inline]
   sctp_do_sm+0x197d/0x5310 net/sctp/sm_sideeffect.c:1170
   sctp_primitive_SEND+0x9f/0xc0 net/sctp/primitive.c:163
   sctp_sendmsg_to_asoc+0x10eb/0x1a30 net/sctp/socket.c:1868
   sctp_sendmsg+0x8d4/0x1d90 net/sctp/socket.c:2026
   inet_sendmsg+0x9d/0xe0 net/ipv4/af_inet.c:825
   sock_sendmsg_nosec net/socket.c:722 [inline]
   sock_sendmsg+0xde/0x190 net/socket.c:745

The fix is to add an unlikely check for the send stream number after the
thread wakes up from the wait_for_sndbuf.

## References
- https://git.kernel.org/stable/c/0443fff49d6352160c200064156c25898bd9f58c
- https://git.kernel.org/stable/c/2584024b23552c00d95b50255e47bd18d306d31a
- https://git.kernel.org/stable/c/667eb99cf7c15fe5b0ecefe75cf658e20ef20c9f
- https://git.kernel.org/stable/c/9346a1a21142357972a6f466ba6275ddc54b04ac
- https://git.kernel.org/stable/c/a615e7270318fa0b98bf1ff38daf6cf52d840312
- https://git.kernel.org/stable/c/b4b6dfad41aaae9e36e44327b18d5cf4b20dd2ce
- https://git.kernel.org/stable/c/d2128636b303aa9cf065055402ee6697409a8837
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53296.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53296
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
