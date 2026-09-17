# [H] nfc: llcp: Fix use-after-free race in nfc_llcp_recv_cc()

## Summary
Severity: High
Advisory: CVE-2026-64010
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64010
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: llcp: Fix use-after-free race in nfc_llcp_recv_cc()

A race condition exists in the NFC LLCP connection state machine where
the connection acceptance packet (CC) can be processed concurrently with
socket release.  This can lead to a use-after-free of the socket object.

When nfc_llcp_recv_cc() moves the socket from the connecting_sockets
list to the sockets list, it does so without holding the socket lock.
If llcp_sock_release() is executing concurrently, it might have already
unlinked the socket and dropped its references, which can result in
nfc_llcp_recv_cc() linking a freed socket into the live list.

Fix this by holding lock_sock() during the state transition and list
movement in nfc_llcp_recv_cc().  After acquiring the lock, check if
the socket is still hashed to ensure it hasn't already been unlinked
and marked for destruction by the release path.  This aligns the locking
pattern with recv_hdlc() and recv_disc().

## References
- https://git.kernel.org/stable/c/0b45c31746e1523d5d482fda8fcf54a35ac417f1
- https://git.kernel.org/stable/c/650bdd8fdfab64a09ee474150313dbc48c374795
- https://git.kernel.org/stable/c/ad8a27d63cac96bac441edd002209ebd996e12fb
- https://git.kernel.org/stable/c/b2a60f7f846faaf5c2cdad4ea6d3a33e5f863183
- https://git.kernel.org/stable/c/b493ea2765cc17cb8aa7e7544a4b6dcb05b6ed77
- https://git.kernel.org/stable/c/bd08bb7443c501d2f2a71d529e4afcf11c9b07d2
- https://git.kernel.org/stable/c/dce85215a6c7b0fd753f577a4c487f647119884c
- https://git.kernel.org/stable/c/ee2d1a8a1833c5e56e9a1745e64b0b4edda732c2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64010.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64010
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
