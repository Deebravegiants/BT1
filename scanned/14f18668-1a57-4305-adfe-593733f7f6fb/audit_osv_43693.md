# [C] sctp: keep chunk->transport in step with the list it is queued on

## Summary
Severity: Critical
Advisory: CVE-2026-74588
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74588
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: keep chunk->transport in step with the list it is queued on

__sctp_outq_flush_rtx() moves a gap-acked chunk onto another transport's
transmitted list without updating chunk->transport:

	if (chunk->tsn_gap_acked) {
		list_move_tail(&chunk->transmitted_list,
			       &transport->transmitted);
		continue;
	}

The chunk then sits on a live transport's list while chunk->transport still
names a different one.  If that transport is removed - sctp_assoc_rm_peer()
from an ASCONF Delete-IP - sctp_transport_free() RCU-frees it and the chunk
is left with a dangling pointer.  sctp_assoc_rm_peer() scrubs
peer->transmitted and asoc->outqueue.out_chunk_list, but the chunk is on
neither.

The pointer is not followed while tsn_gap_acked is set.  A SACK that
reneges on the TSN clears the flag, and the next SACK reaches

	tchunk->transport->flight_size -= sctp_data_size(tchunk);

inside the freed transport.  KASAN reports a slab-use-after-free read in
sctp_check_transmitted(), freed from sctp_assoc_rm_peer().  Both the
removal and the SACKs come from the association peer.

Set chunk->transport at the move.  The ordinary resend path needs nothing:
it reaches its list_move_tail() only after sctp_packet_append_chunk()
returned SCTP_XMIT_OK, and __sctp_packet_append_chunk() has rebound the
chunk by then.

Discovered by XBOW, triaged by Baul Lee <baul.lee@xbow.com>

## References
- https://git.kernel.org/stable/c/1adf929121e13e0b19200bb9fef715b918d483fe
- https://git.kernel.org/stable/c/2b3b5eec8b2c30ee237e3c31a6a38de9c39d804d
- https://git.kernel.org/stable/c/5ccf35ef0ed6059cdf8b1f4606a6584d5b67166b
- https://git.kernel.org/stable/c/6575fb17230814b48b471727c8410c0aadff9274
- https://git.kernel.org/stable/c/6b9e2ea2057113f3393990ba646d2d97c719a80d
- https://git.kernel.org/stable/c/874a7c2b5e184f06134fdfde27e9ce9271bafe58
- https://git.kernel.org/stable/c/9f2cf069a9a72a2d6b97ca8b4c70e714aac99749
- https://git.kernel.org/stable/c/e2e7c1de0e226ca1b7fea2de57a6c9bca408709b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74588.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74588
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
