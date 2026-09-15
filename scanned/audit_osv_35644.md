# [M] NULL pointer dereference in USB DFU device_next download handler (handle_download)

## Summary
Severity: Medium
Advisory: CVE-2026-12051
Aliases: GHSA-vhvq-q6rw-jvm4
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-12051
Type: osv

## Details
The USB DFU class implementation in Zephyr's new (experimental) device_next USB device stack contains a NULL pointer dereference in handle_download() (subsys/usb/device_next/class/usbd_dfu.c). The handler computes MIN(setup->wLength, buf->len) and passes buf->data to the image write callback without checking that the buf net_buf pointer is non-NULL.

The handler is reached over the USB control endpoint, driven by the USB host. For a DFU_DNLOAD (download) request with no Data OUT stage — notably the zero-length terminating download that the DFU protocol uses to end a firmware transfer — the USB core invokes the class handler with a NULL buffer. After the device has been advanced to the DFU_DNLOAD_IDLE state (by sending one valid download block and a GET_STATUS), a zero-length DFU_DNLOAD reaches handle_download() with buf == NULL, dereferencing it.

The result is a NULL+offset read that triggers a fatal CPU fault, i.e. a denial of service (device crash/reset). The attacker is whatever controls the USB host the device is attached to; DFU download support must be enabled with a registered image. There is no memory corruption or information disclosure — impact is limited to availability. The fix adds an explicit if (buf != NULL) guard so the callback receives a zero-length, NULL-data transfer instead of crashing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12051.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-vhvq-q6rw-jvm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-12051
- https://github.com/zephyrproject-rtos/zephyr/commit/552ca371257597b71490482d5cc597157ea60f12
- https://github.com/zephyrproject-rtos/zephyr
