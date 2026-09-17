# [C] nfsd: fix heap overflow in NFSv4.0 LOCK replay cache

## Summary
Severity: Critical
Advisory: CVE-2026-31402
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31402
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.253, >=5.11.0 <5.15.210, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix heap overflow in NFSv4.0 LOCK replay cache

The NFSv4.0 replay cache uses a fixed 112-byte inline buffer
(rp_ibuf[NFSD4_REPLAY_ISIZE]) to store encoded operation responses.
This size was calculated based on OPEN responses and does not account
for LOCK denied responses, which include the conflicting lock owner as
a variable-length field up to 1024 bytes (NFS4_OPAQUE_LIMIT).

When a LOCK operation is denied due to a conflict with an existing lock
that has a large owner, nfsd4_encode_operation() copies the full encoded
response into the undersized replay buffer via read_bytes_from_xdr_buf()
with no bounds check. This results in a slab-out-of-bounds write of up
to 944 bytes past the end of the buffer, corrupting adjacent heap memory.

This can be triggered remotely by an unauthenticated attacker with two
cooperating NFSv4.0 clients: one sets a lock with a large owner string,
then the other requests a conflicting lock to provoke the denial.

We could fix this by increasing NFSD4_REPLAY_ISIZE to allow for a full
opaque, but that would increase the size of every stateowner, when most
lockowners are not that large.

Instead, fix this by checking the encoded response length against
NFSD4_REPLAY_ISIZE before copying into the replay buffer. If the
response is too large, set rp_buflen to 0 to skip caching the replay
payload. The status is still cached, and the client already received the
correct response on the original request.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/0f0e2a54a31a7f9ad2915db99156114872317388
- https://git.kernel.org/stable/c/2665887a69437a8a4f552f69509eecfb73d4aa19
- https://git.kernel.org/stable/c/5133b61aaf437e5f25b1b396b14242a6bb0508e2
- https://git.kernel.org/stable/c/8afb437ea1f70cacb4bbdf11771fb5c4d720b965
- https://git.kernel.org/stable/c/ae8498337dfdfda71bdd0b807c9a23a126011d76
- https://git.kernel.org/stable/c/c9452c0797c95cf2378170df96cf4f4b3bca7eff
- https://git.kernel.org/stable/c/dad0c3c0a8e5d1d6eb0fc455694ce3e25e6c57d0
- https://git.kernel.org/stable/c/f9fcb4441f6c02bb20c2eb340101e27dfe23607c
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31402.json
- https://access.redhat.com/errata/RHSA-2026:10108
- https://access.redhat.com/errata/RHSA-2026:11313
- https://access.redhat.com/errata/RHSA-2026:13565
- https://access.redhat.com/errata/RHSA-2026:13566
- https://access.redhat.com/errata/RHSA-2026:13577
- https://access.redhat.com/errata/RHSA-2026:13578
- https://access.redhat.com/errata/RHSA-2026:13664
- https://access.redhat.com/errata/RHSA-2026:13681
- https://access.redhat.com/errata/RHSA-2026:13734
