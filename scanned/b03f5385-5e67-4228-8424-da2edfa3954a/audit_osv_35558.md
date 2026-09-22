# [M] Deadlock denial of service in USB CDC-NCM device class on TX enqueue failure

## Summary
Severity: Medium
Advisory: CVE-2026-10647
Aliases: GHSA-xcf7-r86m-5q9f
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-10647
Type: osv

## Details
The USB CDC-NCM device class (subsys/usb/device_next/class/usbd_cdc_ncm.c) ignores the return value of usbd_ep_enqueue() in its ethernet transmit callback cdc_ncm_send(). When the enqueue fails, the function still calls k_sem_take(&data->sync_sem, K_FOREVER), blocking on a completion semaphore that is only ever signaled from the bulk-IN transfer-completion callback. Because nothing was enqueued, that callback never fires and the calling thread — a shared network traffic-class TX thread — deadlocks permanently while holding the interface TX lock, halting transmission until reboot (and leaking the transmit buffer).

The enqueue fails under conditions controlled by the attached USB host: usbd_ep_enqueue() returns -EPERM whenever the bus is suspended (a standard, persistent host operation), and the underlying udc_ep_enqueue() returns -EPERM/-ENODEV on disconnect, bus reset, or endpoint disable. The cdc_ncm_send() guard only checks the DATA_IFACE_ENABLED and IFACE_UP flags, not the suspended state, so a packet transmitted while the host holds the bus suspended reaches the failing enqueue and deadlocks the TX path.

The realistic trigger is a bus suspend that occurs while the exported network interface is active and has traffic to send — host sleep, USB selective/auto-suspend, or hub power management — after which any device-originated packet deadlocks the path, recoverable only by reboot. The impact is a persistent loss of the virtual network connection between the host's NCM interface and the Zephyr device; because the deadlocked thread is a shared traffic-class TX thread, egress on other network interfaces can stall as well. There is no memory corruption or information disclosure.

The defect was introduced with the CDC-NCM driver and shipped in releases through v4.4.0; it is fixed by checking the usbd_ep_enqueue() return value and freeing the buffer before the blocking wait.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10647.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-xcf7-r86m-5q9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-10647
- https://github.com/zephyrproject-rtos/zephyr/commit/255bccc1badd1aa06c6e5ddf5b40de8463b33f02
- https://github.com/zephyrproject-rtos/zephyr
