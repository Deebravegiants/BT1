# [H] Use-after-free of GATT subscribe params in Bluetooth host CCC-write response handler

## Summary
Severity: High
Advisory: CVE-2026-10685
Aliases: GHSA-29xh-jm2m-4qvx
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-10685
Type: osv

## Details
The Zephyr Bluetooth GATT client CCC-write response handler gatt_write_ccc_rsp() in subsys/bluetooth/host/gatt.c invoked the application's params->subscribe() callback after it had already called params->notify(conn, params, NULL, 0).

Per the public GATT API, a notify callback with NULL data is the documented signal that the subscription has terminated and the bt_gatt_subscribe_params struct may be freed or reused by the application; calling subscribe() on the struct afterwards is a use-after-free, including an indirect call through the freed params->subscribe function pointer.

The error branch is remotely (adjacent) reachable: a Zephyr device acting as a GATT client that calls bt_gatt_subscribe() can be driven into this ordering when a connected GATT server peer answers the CCC write with an ATT Error Response (the peer-supplied error code flows through att_error_rsp -> att_handle_rsp into gatt_write_ccc_rsp).

For applications that free or recycle subscription parameters in their notification-termination handler, this results in memory corruption, a crash (denial of service), or potentially attacker-influenced control flow. The fix reorders the handler so the subscribe() callback runs before the terminating notify(NULL) in both the error and unsubscribe paths.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10685.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-29xh-jm2m-4qvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-10685
- https://github.com/zephyrproject-rtos/zephyr/commit/c7292f20223637232b6f962141725611a38f6a52
- https://github.com/zephyrproject-rtos/zephyr
