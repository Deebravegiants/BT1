# [H] sctp: validate stream count in sctp_process_strreset_inreq()

## Summary
Severity: High
Advisory: CVE-2026-68315
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68315
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: validate stream count in sctp_process_strreset_inreq()

When processing a RESET_IN_REQUEST from a peer,
sctp_process_strreset_inreq() derives the stream count from the
parameter length but does not check whether the resulting
RESET_OUT_REQUEST would exceed SCTP_MAX_CHUNK_LEN.

The OUT request header (sctp_strreset_outreq, 16 bytes) is 8 bytes
larger than the IN request header (sctp_strreset_inreq, 8 bytes).
Generally, the IP payload is bounded to 65535 bytes, so the stream
list cannot be large enough to trigger the overflow. However, on
interfaces with MTU > 65535 (e.g., loopback with IPv6 jumbograms), a
stream list that fits within the incoming IN parameter can cause a
__u16 overflow in sctp_make_strreset_req() when computing the OUT
request size, leading to an undersized skb allocation and a kernel
BUG:

  net/core/skbuff.c:207         skb_panic
  net/core/skbuff.c:2625        skb_put
  net/sctp/sm_make_chunk.c:1535 sctp_addto_chunk
  net/sctp/sm_make_chunk.c:3695 sctp_make_strreset_req
  net/sctp/stream.c:655         sctp_process_strreset_inreq

The local setsockopt path validates the generated reset request size.
However, for an incoming-only reset, it accounts for the smaller IN
request even though the peer must generate an OUT request with the same
stream list. Such a request cannot be completed successfully by the
peer.

Reject peer IN requests whose corresponding OUT request would exceed
SCTP_MAX_CHUNK_LEN. Also tighten the local check so it does not send an
IN request that would require an oversized OUT request from the peer.

## References
- https://git.kernel.org/stable/c/00ae679cb21a035491fdad8d58dc6d79cc68b675
- https://git.kernel.org/stable/c/18ae07691d43183d270de8be9dc8e027906015d9
- https://git.kernel.org/stable/c/1a10fe1aa9c01f41b389a31906a77d538637c9d9
- https://git.kernel.org/stable/c/60c47dea5d320d2fc706e9aad1db38a04df0a056
- https://git.kernel.org/stable/c/61327d8e7cfb0259d527be17202630f556213249
- https://git.kernel.org/stable/c/6f0e39d180cd7cced647381b6fa14fd83d261047
- https://git.kernel.org/stable/c/7cf7439948e3bf639119119922c88ec190874ca3
- https://git.kernel.org/stable/c/b255d8cd6cc68045ae9eecbac3b3c14e1f176c9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68315.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68315
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
