# [H] Bluetooth: eir: Fix stack OOB write when prepending the Flags AD

## Summary
Severity: High
Advisory: CVE-2026-64539
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64539
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <6.1.178, >=6.2.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: eir: Fix stack OOB write when prepending the Flags AD

eir_create_adv_data() builds the advertising data into a fixed-size
buffer ("size", 31 for the legacy path). It may prepend a 3-byte "Flags"
AD structure (LE_AD_NO_BREDR on an LE-only controller) and then copies
the per-instance data without checking that it still fits:

	memcpy(ptr, adv->adv_data, adv->adv_data_len);

tlv_data_max_len() only reserves those 3 bytes when the user-supplied
flags carry a managed-flags bit, so an instance added with flags == 0 is
accepted with adv_data_len up to the full buffer. At advertise time the
flags are still prepended, and the memcpy() writes 3 + adv_data_len
bytes into the size-byte buffer:

  BUG: KASAN: stack-out-of-bounds in eir_create_adv_data (net/bluetooth/eir.c:301)
  Write of size 31 at addr ffff88800a547bdc by task kworker/u9:0/65
  Workqueue: hci0 hci_cmd_sync_work
   __asan_memcpy (mm/kasan/shadow.c:106)
   eir_create_adv_data (net/bluetooth/eir.c:301)
   hci_update_adv_data_sync (net/bluetooth/hci_sync.c:1310)
   hci_schedule_adv_instance_sync (net/bluetooth/hci_sync.c:1817)
   hci_cmd_sync_work (net/bluetooth/hci_sync.c:332)
  This frame has 1 object:
   [32, 64) 'cp'

The "Flags" structure is added by the kernel, not requested by
userspace, so only prepend it when it fits together with the instance
advertising data; when there is no room for both, drop the flags rather
than the user-provided data.

Reachable by a local user with CAP_NET_ADMIN owning an LE-only
controller on the legacy advertising path.

## References
- https://git.kernel.org/stable/c/09301f1fdf2aef8cce34d0c4650c30e7edb1ced9
- https://git.kernel.org/stable/c/0f0b6232af56441d0a2dcb173cc4f8d8aab39014
- https://git.kernel.org/stable/c/57077eeb586c42f124bc09e018449362223067b3
- https://git.kernel.org/stable/c/6f5fb689fdf80bdd143f22a502f9eb1f3c85e286
- https://git.kernel.org/stable/c/f1b4df9c260c51726da2e86e19322825fddeefd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64539.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64539
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
