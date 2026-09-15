# [H] ice: fix double-free of tx_buf skb

## Summary
Severity: High
Advisory: CVE-2026-53009
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53009
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix double-free of tx_buf skb

If ice_tso() or ice_tx_csum() fail, the error path in
ice_xmit_frame_ring() frees the skb, but the 'first' tx_buf still points
to it and is marked as valid (ICE_TX_BUF_SKB).
'next_to_use' remains unchanged, so the potential problem will
likely fix itself when the next packet is transmitted and the tx_buf
gets overwritten. But if there is no next packet and the interface is
brought down instead, ice_clean_tx_ring() -> ice_unmap_and_free_tx_buf()
will find the tx_buf and free the skb for the second time.

The fix is to reset the tx_buf type to ICE_TX_BUF_EMPTY in the error
path, so that ice_unmap_and_free_tx_buf().
Move the initialization of 'first' up, to ensure it's already valid in
case we hit the linearization error path.

The bug was spotted by AI while I had it looking for something else.
It also proposed an initial version of the patch.

I reproduced the bug and tested the fix by adding code to inject
failures, on a build with KASAN.

I looked for similar bugs in related Intel drivers and did not find any.

## References
- https://git.kernel.org/stable/c/1a303baa715e6b78d6a406aaf335f87ff35acfcd
- https://git.kernel.org/stable/c/4c08fc2119ef0281cfa2cee007acf0a251be55f2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53009.json
- https://access.redhat.com/errata/RHSA-2026:42919
- https://access.redhat.com/errata/RHSA-2026:54246
- https://access.redhat.com/errata/RHSA-2026:54247
- https://access.redhat.com/errata/RHSA-2026:65711
- https://access.redhat.com/errata/RHSA-2026:65712
- https://access.redhat.com/security/cve/CVE-2026-53009
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53009.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53009
- https://bugzilla.redhat.com/show_bug.cgi?id=2492390
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
