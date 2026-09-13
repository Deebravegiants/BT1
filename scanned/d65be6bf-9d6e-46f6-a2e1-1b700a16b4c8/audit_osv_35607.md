# [H] Use-after-free in Bluetooth host ATT TX completion on disconnect mid-transfer

## Summary
Severity: High
Advisory: CVE-2026-11368
Aliases: GHSA-85vg-gwc4-77g7
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-11368
Type: osv

## Details
The Bluetooth host ATT layer (subsys/bluetooth/host/att.c) associates each in-flight ATT TX buffer with its owning channel via the static tx_meta_data_storage[] array (data->att_chan = chan). When a buffer's last reference is dropped, its net-buf destroy callback defers the completion handling to the system workqueue (att_tx_destroy -> att_tx_destroy_work_handler -> att_on_sent_cb -> bt_att_sent), where bt_att_sent dereferences the channel and its ATT context (sys_slist_get(&att->reqs)).

When a peer disconnects while an ATT PDU (a server notification/indication or any response) is still in flight in the controller TX path, L2CAP tears the channel down in l2cap_chan_del(): it runs the disconnected callback and then the released callback (bt_att_released), which frees the channel slab slot. Because the in-flight buffer is held by the connection TX path rather than the channel's own queue, its deferred destroy work can run after the channel has been freed. The att_on_sent_cb guard intended to drop the stale callback itself dereferences meta->att_chan, which is now a dangling pointer into a freed (and possibly reused) slab slot.

A remote peer with an ATT connection can drive this by disconnecting during routine ATT traffic; no pairing or user interaction is required to reach the ATT bearer. The result is a use-after-free read/write of freed channel memory, reliably crashing the Bluetooth host (denial of service) and, because the channel slab slot may be reused, potentially corrupting live memory.

The fix makes bt_att_released() NULL the att_chan field of every tx_meta_data_storage[] entry still referencing the channel before freeing it, so the deferred guard observes a NULL pointer and drops the callback. Teardown and the destroy work both run on the cooperative system workqueue, so the array update is serialized and needs no lock.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11368.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-85vg-gwc4-77g7
- https://nvd.nist.gov/vuln/detail/CVE-2026-11368
- https://github.com/zephyrproject-rtos/zephyr/commit/dfdea9bad8d9b5b31c125e97fcffb549f2217caa
- https://github.com/zephyrproject-rtos/zephyr
