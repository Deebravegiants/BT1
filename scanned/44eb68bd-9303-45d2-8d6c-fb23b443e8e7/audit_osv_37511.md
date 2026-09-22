# [H] Bluetooth: hci_event: move wake reason storage into validated event handlers

## Summary
Severity: High
Advisory: CVE-2026-31771
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31771
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_event: move wake reason storage into validated event handlers

hci_store_wake_reason() is called from hci_event_packet() immediately
after stripping the HCI event header but before hci_event_func()
enforces the per-event minimum payload length from hci_ev_table.
This means a short HCI event frame can reach bacpy() before any bounds
check runs.

Rather than duplicating skb parsing and per-event length checks inside
hci_store_wake_reason(), move wake-address storage into the individual
event handlers after their existing event-length validation has
succeeded. Convert hci_store_wake_reason() into a small helper that only
stores an already-validated bdaddr while the caller holds hci_dev_lock().
Use the same helper after hci_event_func() with a NULL address to
preserve the existing unexpected-wake fallback semantics when no
validated event handler records a wake address.

Annotate the helper with __must_hold(&hdev->lock) and add
lockdep_assert_held(&hdev->lock) so future call paths keep the lock
contract explicit.

Call the helper from hci_conn_request_evt(), hci_conn_complete_evt(),
hci_sync_conn_complete_evt(), le_conn_complete_evt(),
hci_le_adv_report_evt(), hci_le_ext_adv_report_evt(),
hci_le_direct_adv_report_evt(), hci_le_pa_sync_established_evt(), and
hci_le_past_received_evt().

## References
- https://git.kernel.org/stable/c/2b2bf47cd75518c36fa2d41380e4a40641cc89cd
- https://git.kernel.org/stable/c/86c8d07a64d553c41e213b52650020010f9ef23e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31771.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31771
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
