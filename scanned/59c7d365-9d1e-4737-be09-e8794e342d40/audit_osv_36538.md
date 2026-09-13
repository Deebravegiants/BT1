# [M] Bluetooth GATT notify/indicate enforces the wrong attribute's permissions, bypassing encryption/authentication requirements on characteristic values

## Summary
Severity: Medium
Advisory: CVE-2026-2411
Aliases: GHSA-4w3r-v9q9-4462
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-2411
Type: osv

## Details
Zephyr's Bluetooth host declares a GATT characteristic as two consecutive attributes: a Characteristic Declaration whose permission is hard-coded to BT_GATT_PERM_READ, and a Characteristic Value attribute that carries the application-specified security permissions (e.g. BT_GATT_PERM_READ_ENCRYPT / READ_AUTHEN / READ_LESC). The public notify and indicate APIs explicitly accept either attribute, and passing the declaration is the documented, common idiom. Before sending each notification or indication, the host re-checks link security with bt_gatt_check_perm() against params->attr in gatt_notify(), gatt_indicate(), and gatt_notify_multiple_verify_params() (subsys/bluetooth/host/gatt.c).

When the application passed the Characteristic Declaration attribute, the host correctly redirected the value handle but left params->attr pointing at the declaration, so the security check evaluated the declaration's permissions (no security required) instead of the value's. As a result the encryption/authentication/LESC requirement configured on the characteristic value was skipped. The Notify-Multiple path additionally used a mask that omitted the LE Secure Connections requirement.

A remote peer triggers the disclosure by connecting (optionally without pairing or encryption) and writing the Client Characteristic Configuration descriptor to enable notifications or indications, causing the server to emit the protected value over a link that has not reached the required security level. The impact is information disclosure / access-control bypass for characteristic values the application intended to expose only over a secured link; exposure depends on the application declaring encrypt/authen-required notify/indicate characteristics and on the CCC being writable at a lower security tier. There is no memory-safety or availability impact.

The fix adds bt_gatt_attr_resolve_value(), which maps a declaration attribute to the following value attribute before the permission check, and switches the Notify-Multiple path to the full BT_GATT_PERM_READ_ENCRYPT_MASK so the LESC requirement is also enforced.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2411.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-4w3r-v9q9-4462
- https://nvd.nist.gov/vuln/detail/CVE-2026-2411
- https://github.com/zephyrproject-rtos/zephyr/commit/c3386f92fe81bd10dc23e6a115e6a80a7d863546
- https://github.com/zephyrproject-rtos/zephyr
