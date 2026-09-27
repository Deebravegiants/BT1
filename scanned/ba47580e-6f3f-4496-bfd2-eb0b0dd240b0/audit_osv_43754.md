# [C] sctp: clear control chunk transport if it is being removed

## Summary
Severity: Critical
Advisory: CVE-2026-74688
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74688
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: clear control chunk transport if it is being removed

sctp_make_heartbeat_ack() caches the destination transport in
chunk->transport without taking a reference. When src_out_of_asoc_ok is
enabled, the HEARTBEAT ACK may remain queued on control_chunk_list instead
of being transmitted immediately.

If the peer transport is removed while the chunk is still queued,
sctp_assoc_rm_peer() drops the transport and schedules it for RCU freeing,
but only clears cached transport pointers in out_chunk_list.  The queued
control chunk therefore retains a dangling transport pointer.

Once an ASCONF_ACK clears the suppression and the queued control chunk is
transmitted, SCTP dereferences the stale transport pointer, leading to a
use-after-free.

Fix this by also clearing chunk->transport for queued control chunks in
control_chunk_list when removing the transport.

## References
- https://git.kernel.org/stable/c/18d704bdd809377dfd81a3c2f42426763b5da227
- https://git.kernel.org/stable/c/4d6b9cac6df5e0cfef1a66b3edd7aebdb9e4b7e7
- https://git.kernel.org/stable/c/6160e756db81d6cb63e3e2952efcf6c5134be385
- https://git.kernel.org/stable/c/8de65194a04d2552cd39b6c67d942d490f22d174
- https://git.kernel.org/stable/c/936658ec41c28c397ef390140e02d4c91ade92f0
- https://git.kernel.org/stable/c/c9158ceaf27780ef64534ad72f44ffde3f8ccc49
- https://git.kernel.org/stable/c/dbb3f418a8665ffb0514e1a9520ab6a1c5d4d886
- https://git.kernel.org/stable/c/fad4766a74220fe579c6fcaa10ba01c23529814f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74688.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74688
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
