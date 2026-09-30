# [C] wifi: iwlwifi: mld: fix TSO segmentation explosion when AMSDU is disabled

## Summary
Severity: Critical
Advisory: CVE-2026-64037
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64037
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mld: fix TSO segmentation explosion when AMSDU is disabled

When the TLC notification disables AMSDU for a TID, the MLD driver sets
max_tid_amsdu_len to the sentinel value 1. The TSO segmentation path in
iwl_mld_tx_tso_segment() checks for zero but not for this sentinel,
allowing it to reach the num_subframes calculation:

  num_subframes = (max_tid_amsdu_len + pad) / (subf_len + pad)
                = (1 + 2) / (1534 + 2) = 0

This zero propagates to iwl_tx_tso_segment() which sets:

  gso_size = num_subframes * mss = 0

Calling skb_gso_segment() with gso_size=0 creates over 32000 tiny
segments from a single GSO skb. This floods the TX ring with ~1024
micro-frames (the rest are purged), creating a massive burst of TX
completion events that can lead to memory corruption and a subsequent
use-after-free in TCP's retransmit queue (refcount underflow in
tcp_shifted_skb, NULL deref in tcp_rack_detect_loss).

The MVM driver is immune because it checks mvmsta->amsdu_enabled before
reaching the num_subframes calculation. The MLD driver has no equivalent
bitmap check and relies solely on max_tid_amsdu_len, which does not
catch the sentinel value.

Fix this by detecting the sentinel value (max_tid_amsdu_len == 1) at the
existing check and falling back to non-AMSDU TSO segmentation. Also add
a WARN_ON_ONCE guard after the num_subframes division as defense-in-depth
to catch any future code paths that produce zero through a different
mechanism.

## References
- https://git.kernel.org/stable/c/92cee08dc4f00e77fd1317e4343c5d458b0abab7
- https://git.kernel.org/stable/c/9e360e610a73f62432e986775023d5382773f045
- https://git.kernel.org/stable/c/cbe1c8245e4469d1aa6e12e5d913611376d23788
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64037.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64037
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
