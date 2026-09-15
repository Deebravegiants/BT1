# [H] xsk: cache csum_start/csum_offset to fix TOCTOU in xsk_skb_metadata()

## Summary
Severity: High
Advisory: CVE-2026-53250
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53250
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: cache csum_start/csum_offset to fix TOCTOU in xsk_skb_metadata()

The TX metadata area resides in the UMEM buffer which is memory-mapped
and concurrently writable by userspace. In xsk_skb_metadata(),
csum_start and csum_offset are read from shared memory for bounds
validation, then read again for skb assignment. A malicious userspace
application can race to overwrite these values between the two reads,
bypassing the bounds check and causing out-of-bounds memory access
during checksum computation in the transmit path.

Fix this by reading csum_start and csum_offset into local variables
once, then using the local copies for both validation and assignment.

Note that other metadata fields (flags, launch_time) and the cached
csum fields may be mutually inconsistent due to concurrent userspace
writes, but this is benign: the only security-critical invariant is
that each field's validated value is the same one used, which local
caching guarantees.

## References
- https://git.kernel.org/stable/c/0dfe05b938435892875e07771170051346412df9
- https://git.kernel.org/stable/c/22ba97ea9cc1f63a0d0244fae38057ed452b6ac7
- https://git.kernel.org/stable/c/bfdfd2706d5fb2cd496a1506e680daf979309c8b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53250.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53250
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
