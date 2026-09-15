# [H] wifi: ath12k: fix out-of-bounds clear_bit in ath12k_mac_dp_peer_cleanup()

## Summary
Severity: High
Advisory: CVE-2026-74554
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74554
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix out-of-bounds clear_bit in ath12k_mac_dp_peer_cleanup()

ath12k_mac_dp_peer_cleanup() clears the ML peer ID slot on the
free_ml_peer_id_map bitmap by indexing it with dp_peer->peer_id. That is
wrong: dp_peer->peer_id for an MLO peer always carries the
ATH12K_PEER_ML_ID_VALID bit (BIT(13)), so clear_bit() is invoked with
index >= 0x2000, which is far outside the bitmap of ATH12K_MAX_MLO_PEERS
(256) bits and corrupts memory adjacent to ah->free_ml_peer_id_map. The
intended bitmap entry also never gets cleared, so subsequent
ath12k_peer_ml_alloc() calls eventually run out of IDs.

The ID without the VALID bit is what ath12k_peer_ml_alloc() returned and
is stored in ahsta->ml_peer_id. Use that instead.

While there, also reset ahsta->ml_peer_id to ATH12K_MLO_PEER_ID_INVALID so
the bitmap and ahsta->ml_peer_id stay in sync.

Tested-on: WCN7850 hw2.0 PCI WLAN.HMT.1.1.c5-00302-QCAHMTSWPL_V1.0_V2.0_SILICONZ-1.115823.3

## References
- https://git.kernel.org/stable/c/234b5cb81e6fcc1e3b31b13deff66130be55f36e
- https://git.kernel.org/stable/c/47abd2ca281531deee38a3b3770d885e270e9fc9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74554.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74554
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
