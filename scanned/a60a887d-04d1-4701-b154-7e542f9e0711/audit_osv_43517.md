# [H] Bluetooth: hci_core: Fix UAF in hci_unregister_dev()

## Summary
Severity: High
Advisory: CVE-2026-74302
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74302
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_core: Fix UAF in hci_unregister_dev()

hci_unregister_dev() does not disable cmd_timer and ncmd_timer
before the hci_dev structure is freed. If a timeout fires
during device teardown, the callback dereferences freed memory
(including the hdev->reset function pointer), leading to a
use-after-free.

Add disable_delayed_work_sync() calls alongside the existing
disable_work_sync() calls to ensure both timers are fully
quiesced before teardown proceeds.

## References
- https://git.kernel.org/stable/c/48c7ad6afcc58c2cda11fed39791708103b6a644
- https://git.kernel.org/stable/c/5edcc018fa6e80b2c478454a4a8229c23d67c181
- https://git.kernel.org/stable/c/672d52d9412252e61b8de8d773ccdf5a277cf540
- https://git.kernel.org/stable/c/a0fd1086a57b982f8c24ae4ab165c2af39fe1735
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74302.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
