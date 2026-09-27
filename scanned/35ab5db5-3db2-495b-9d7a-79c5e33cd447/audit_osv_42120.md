# [C] sctp: validate STALE_COOKIE cause length before reading staleness

## Summary
Severity: Critical
Advisory: CVE-2026-64551
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64551
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: validate STALE_COOKIE cause length before reading staleness

When an ERROR chunk with a STALE_COOKIE cause is received in the
COOKIE_ECHOED state, sctp_sf_do_5_2_6_stale() reads the 4-byte Measure
of Staleness that follows the cause header:

	err   = (struct sctp_errhdr *)(chunk->skb->data);
	stale = ntohl(*(__be32 *)((u8 *)err + sizeof(*err)));

err is the first cause in the chunk, not the STALE_COOKIE cause that
caused the dispatch, and nothing guarantees the staleness field is
present. sctp_walk_errors() only requires a cause to be as long as the
4-byte header, so for a STALE_COOKIE cause of length 4 the read runs
past the cause, and for a minimal ERROR chunk past skb->tail. The value
is echoed to the peer in the Cookie Preservative of the reply INIT,
leaking uninitialized memory.

sctp_sf_cookie_echoed_err() already walks to the STALE_COOKIE cause, so
check its length there and pass it to sctp_sf_do_5_2_6_stale(), which
reads that cause instead of the first one. A STALE_COOKIE cause too
short to hold the staleness field is discarded.

The read is reachable by any peer that can drive an association into
COOKIE_ECHOED, including an unprivileged process using a raw SCTP socket
in a user and network namespace.

## References
- https://git.kernel.org/stable/c/08a8f2d13f703924316e9aeac863a88ef50990c7
- https://git.kernel.org/stable/c/1cd23ca80784223fa2204e16203f754da4e821f8
- https://git.kernel.org/stable/c/588706ebaf8cdb4a4161602949eba365514b1db1
- https://git.kernel.org/stable/c/6022da37786701df1fc5dd946a6dcba59d5473b1
- https://git.kernel.org/stable/c/861f884f5471632c731cbbd612a1c072e391a624
- https://git.kernel.org/stable/c/a257b41ddfe9e327b26581ad2777f04b23ac73f5
- https://git.kernel.org/stable/c/bbd6b2ea966cf57b6ae095cf5a8dbc993cd197a0
- https://git.kernel.org/stable/c/ebe0a55d954fa8da383b6192edb8f763dcb002d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64551.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64551
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
