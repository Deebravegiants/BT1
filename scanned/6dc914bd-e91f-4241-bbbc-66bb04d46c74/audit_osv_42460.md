# [H] Bluetooth: hci_sync: Protect UUID list traversal

## Summary
Severity: High
Advisory: CVE-2026-68189
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68189
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: Protect UUID list traversal

The hci_sync conversion moved class-of-device and EIR generation from an
HCI request built under hdev->lock to asynchronous command sync work.
The worker holds hdev->req_lock, but that lock does not serialize access
to hdev->uuids against add_uuid() and remove_uuid(), which update the
list under hdev->lock.

The following interleaving can therefore occur:

  CPU0 (command sync work)       CPU1 (management socket)
  fetch uuid from the list
                                list_del(&uuid->list)
                                kfree(uuid)
  read uuid->size

KASAN reports the resulting use-after-free:

  BUG: KASAN: slab-use-after-free in eir_create+0xb8f/0xee0
  Read of size 1 at addr ffff88810dbd8620 by task kworker/u17:0/87
  Workqueue: hci0 hci_cmd_sync_work
  Call Trace:
   eir_create+0xb8f/0xee0
   hci_update_eir_sync+0x1c0/0x330
   hci_cmd_sync_work+0x13c/0x290
   process_one_work+0x63a/0x1070
   worker_thread+0x45b/0xd10

  Allocated by task 86:
   __kasan_kmalloc+0x8f/0xa0
   add_uuid+0x18a/0x4b0
   hci_sock_sendmsg+0x1033/0x1ea0

  Freed by task 92:
   __kasan_slab_free+0x43/0x70
   kfree+0x131/0x3c0
   remove_uuid+0x25e/0x560
   hci_sock_sendmsg+0x1033/0x1ea0

Hold hdev->lock while generating and committing the class-of-device and
EIR snapshots.  Release it before sending an HCI command, so controller
waits do not happen under the device lock.  This protects all UUID list
walks in these paths and restores the serialization lost in the command
sync conversion.

## References
- https://git.kernel.org/stable/c/30bc6248f035a792d1b1f4cc761b32fd5827b55f
- https://git.kernel.org/stable/c/a351f68fb24828b23a971e00b8238ee0e8a40380
- https://git.kernel.org/stable/c/a42f5536ea9c00e13f0c0fbb330feed95e2365ca
- https://git.kernel.org/stable/c/e4fa2c5c261d736b8e58759fdef3a968d510630c
- https://git.kernel.org/stable/c/e9027ffbf5a0f3c12ca8900822e884eae9f0821b
- https://git.kernel.org/stable/c/fe13adc258df88d95789e5673c7ba5178b5f8b28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68189.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68189
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
