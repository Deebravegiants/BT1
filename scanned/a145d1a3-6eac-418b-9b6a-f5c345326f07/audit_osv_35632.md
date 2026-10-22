# [M] Double-free / use-after-free in Realtek BEE Bluetooth HCI driver `send()` error paths

## Summary
Severity: Medium
Advisory: CVE-2026-11894
Aliases: GHSA-v9mj-h2m6-v9c6
CVSS: 5.9 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-11894
Type: osv

## Details
The Realtek BEE Bluetooth HCI driver's send callback, bt_hci_bee_send() in drivers/bluetooth/hci/hci_bee.c, violated the bt_hci_driver_api buffer-ownership contract. That contract requires the driver to consume (unref) the transmit net_buf only on success; on an error return the host caller retains ownership and unrefs the buffer itself. The pre-fix code routed all error paths through a shared cleanup label that unconditionally called net_buf_unref(buf) before returning the error code.

Because the host TX paths (in subsys/bluetooth/host/hci_core.c) unref the buffer again after send() returns an error, the buffer is freed twice: the driver returns it to its net_buf pool and the host then unrefs the already-freed buffer, corrupting the shared pool / underflowing the reference count (CWE-415). The same error branch additionally dereferenced buf->len inside a LOG_ERR call after the buffer had already been unref'd, a read of freed memory (CWE-416) that is compiled in at the default error log level.

The failing edges are reached when the controller's host-to-controller buffer allocation fails or the controller send fails (resource-exhaustion / IO conditions). A remote Bluetooth peer can push the device toward these conditions indirectly by driving heavy host transmit activity, at which point the double-free corrupts the host net_buf pool and most likely crashes the device, with residual potential for further memory corruption. The impact is confined to builds using this specific Realtek BEE HCI driver.

The fix returns early from each error path without unreffing and unrefs the buffer only on the success path, restoring the ownership contract and eliminating both the double-free and the use-after-free read.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11894.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-v9mj-h2m6-v9c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-11894
- https://github.com/zephyrproject-rtos/zephyr/commit/9a684b5c314fb1d8670b01f7b6c4450a9353906c
- https://github.com/zephyrproject-rtos/zephyr
