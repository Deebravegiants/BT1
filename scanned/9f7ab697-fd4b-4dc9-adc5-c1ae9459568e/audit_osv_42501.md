# [C] sctp: auth: verify auth requirement when auth_chunk is NULL

## Summary
Severity: Critical
Advisory: CVE-2026-68300
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68300
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: auth: verify auth requirement when auth_chunk is NULL

sctp_auth_chunk_verify() returns true unconditionally when
chunk->auth_chunk is NULL, silently skipping authentication.
This is incorrect when:

1. skb_clone() failed in the BH receive path, leaving auth_chunk
   NULL. In sctp_endpoint_bh_rcv() asoc is NULL for new
   connections, so the early sctp_auth_recv_cid() check cannot
   catch this.

2. No AUTH chunk precedes COOKIE-ECHO, so skb_clone() is never
   called and auth_chunk remains NULL.

Fix by checking sctp_auth_recv_cid() when auth_chunk is NULL:
if authentication is required, return false to drop the chunk;
otherwise continue normally.

## References
- https://git.kernel.org/stable/c/18957373920caf5cdaf5cf32e5d1d7a99ca7700a
- https://git.kernel.org/stable/c/28c5fdce9dd955d2baf5e28987819b6d7cfaf646
- https://git.kernel.org/stable/c/5a022ac51ad83b4ce6c898f4b9eefc65bd26b247
- https://git.kernel.org/stable/c/6caf0e8590c0bf05a76b0d387726adf3a6f3725c
- https://git.kernel.org/stable/c/83f5031f2a6a49d696eb4cc0898345d12f9c6451
- https://git.kernel.org/stable/c/8e04823c120b376ef7dab14b60ebf6823aa16c14
- https://git.kernel.org/stable/c/a129792b3aef15002746c13522781d92ed3522c3
- https://git.kernel.org/stable/c/ec2e157fc9678a9bc411305a25aec3fd337d7efb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68300.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
