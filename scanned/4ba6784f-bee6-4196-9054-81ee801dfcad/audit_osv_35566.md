# [M] Use-after-free / double-free of the root USB device in the experimental USB host stack

## Summary
Severity: Medium
Advisory: CVE-2026-10663
Aliases: GHSA-26q8-xjq3-f5p6
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-12
Source: https://osv.dev/vulnerability/CVE-2026-10663
Type: osv

## Details
In Zephyr's experimental USB host stack (CONFIG_USB_HOST_STACK), usbh_device_disconnect() (subsys/usb/host/usbh_device.c) freed the root usb_device slab object without clearing the cached pointer ctx->root. The bus removal handler dev_removed_handler() (subsys/usb/host/usbh_core.c) decides what to tear down solely from ctx->root, checking only that it is non-NULL.

Because UHC controller drivers (e.g. uhc_max3421e, uhc_mcux_common) synthesize UHC_EVT_DEV_REMOVED directly from physical bus line state with no debounce or state guard, an attacker with physical USB access (or a rogue device that bounces its connection) can deliver a second device-removed event after a root device disconnect. The handler then re-enters usbh_device_disconnect() with the dangling pointer, locking a mutex inside the freed object (use-after-free), removing the freed node from the device list, and calling k_mem_slab_free() on the already-freed block (double-free). If the slab block has been reissued to a newly attached device in between, this corrupts a live object.

Impact is denial of service (crash) and memory corruption; the attack vector is physical/local. The flaw was introduced in v4.4.0 by the connect/disconnect refactor and is fixed by clearing ctx->root in usbh_device_disconnect() before freeing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10663.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-26q8-xjq3-f5p6
- https://nvd.nist.gov/vuln/detail/CVE-2026-10663
- https://github.com/zephyrproject-rtos/zephyr/commit/4b87a8f161a44cb19505fa97db7cf72f64d49165
- https://github.com/zephyrproject-rtos/zephyr
