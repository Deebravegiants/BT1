# [H] wifi: iwlwifi: mld: stop TX during firmware restart

## Summary
Severity: High
Advisory: CVE-2026-64175
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64175
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mld: stop TX during firmware restart

When iwlwifi firmware crashes (e.g., NMI_INTERRUPT_UNKNOWN on Intel
BE201/Wi-Fi 7), iwl_mld_nic_error() sets mld->fw_status.in_hw_restart
to true. However, iwl_mld_tx_from_txq() does not check this flag before
dequeuing frames from mac80211 and pushing them to the transport layer.

Since the firmware is dead, iwl_trans_tx() returns -EIO for each frame,
which then gets freed immediately. Under high-throughput conditions
(e.g., Tailscale UDP traffic or active SSH sessions), this creates a
tight dequeue-send-fail-free loop that wastes CPU cycles and generates
rapid skb allocation churn, leading to memory pressure from slab
fragmentation.

The RX path already has this guard (iwl_mld_rx_mpdu checks
in_hw_restart at rx.c:1906), and so does the TXQ allocation worker
(iwl_mld_add_txqs_wk at tx.c:156). Add the same guard to
iwl_mld_tx_from_txq() to stop all TX during firmware restart.

Frames left in mac80211's TXQs are naturally drained after restart
completes, when queue reallocation triggers iwl_mld_tx_from_txq()
via iwl_mld_add_txq_list(), or when new upper-layer traffic invokes
wake_tx_queue.

Tested on ASUS Zenbook 14 UX3405CA with Intel BE201 (Wi-Fi 7) on
kernel 6.19.5 where the firmware crashes approximately every 10-15
minutes under Tailscale traffic.

## References
- https://git.kernel.org/stable/c/13f1786395dbbf3df73337063c798f1266be6151
- https://git.kernel.org/stable/c/2becb38a3e217ef2b2f42fddd7db7a25905ec291
- https://git.kernel.org/stable/c/dc31c69476520bb4c2a208211a8d3c310a62c4d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64175.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64175
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
