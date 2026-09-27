# [H] wifi: ath6kl: fix OOB read from firmware num_msg in TX complete handler

## Summary
Severity: High
Advisory: CVE-2026-68353
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68353
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath6kl: fix OOB read from firmware num_msg in TX complete handler

The firmware-controlled num_msg field (u8, 0-255) drives the loop in
ath6kl_wmi_tx_complete_event_rx() without validation against the buffer
length. This allows out-of-bounds reads of up to 1020 bytes past the
WMI event buffer when the firmware sends an inflated num_msg.

Add a check that the buffer is large enough to hold the fixed struct
and the num_msg variable-length entries.

## References
- https://git.kernel.org/stable/c/0e0fc04af9b443c6b425f00fb604ff599bc80d1d
- https://git.kernel.org/stable/c/289edc3c71344b89e6522891147cfb8f61b088bb
- https://git.kernel.org/stable/c/35196a07603f8c94a4943093bc26d5b5826285f8
- https://git.kernel.org/stable/c/3a21c89215cc18f1a97c5e5bfd1da6d4f3d44495
- https://git.kernel.org/stable/c/5297299c3fa6133275db0be99d69cd759b6cbfe9
- https://git.kernel.org/stable/c/69ac7ba3a3df6654e7daa82674575a8c4a1a63ea
- https://git.kernel.org/stable/c/c38b0d5c661951b5dd082bdf31f8a57a0ce6e540
- https://git.kernel.org/stable/c/eb636fbc443149b3501c3f97e26225ddcb314a0f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68353.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68353
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
