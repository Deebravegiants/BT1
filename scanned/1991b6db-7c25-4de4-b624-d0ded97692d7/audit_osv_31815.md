# [H] Bluetooth: btusb: mediatek: Add locks for usb_driver_claim_interface()

## Summary
Severity: High
Advisory: CVE-2025-21827
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2025-21827
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btusb: mediatek: Add locks for usb_driver_claim_interface()

The documentation for usb_driver_claim_interface() says that "the
device lock" is needed when the function is called from places other
than probe(). This appears to be the lock for the USB interface
device. The Mediatek btusb code gets called via this path:

  Workqueue: hci0 hci_power_on [bluetooth]
  Call trace:
   usb_driver_claim_interface
   btusb_mtk_claim_iso_intf
   btusb_mtk_setup
   hci_dev_open_sync
   hci_power_on
   process_scheduled_works
   worker_thread
   kthread

With the above call trace the device lock hasn't been claimed. Claim
it.

Without this fix, we'd sometimes see the error "Failed to claim iso
interface". Sometimes we'd even see worse errors, like a NULL pointer
dereference (where `intf->dev.driver` was NULL) with a trace like:

  Call trace:
   usb_suspend_both
   usb_runtime_suspend
   __rpm_callback
   rpm_suspend
   pm_runtime_work
   process_scheduled_works

Both errors appear to be fixed with the proper locking.

## References
- https://git.kernel.org/stable/c/4194766ec8756f4f654d595ae49962acbac49490
- https://git.kernel.org/stable/c/930e1790b99e5839e1af69d2f7fd808f1fba2df9
- https://git.kernel.org/stable/c/e9087e828827e5a5c85e124ce77503f2b81c3491
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21827.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21827
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
