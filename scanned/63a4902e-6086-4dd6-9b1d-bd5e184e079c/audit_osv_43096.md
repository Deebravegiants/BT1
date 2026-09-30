# [H] i3c: mipi-i3c-hci: Fix race in i3c_hci_addr_to_dev()

## Summary
Severity: High
Advisory: CVE-2026-72454
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72454
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

i3c: mipi-i3c-hci: Fix race in i3c_hci_addr_to_dev()

i3c_hci_addr_to_dev() walks bus->devs.i3c, which is protected by
bus.lock (rwsem).  However, it is invoked from the MIPI I3C HCI IRQ
handler, which cannot take bus.lock.  This allows concurrent device
addition/removal in the I3C core to modify the list while it is being
traversed, potentially leading to use-after-free or crashes.

Remove the dependency on the bus device list and introduce a dedicated
lookup table.  Add an ibi_devs[] array indexed by DAT entry, maintained
under hci->lock.  Update the array when IBIs are enabled or disabled,
so that it always reflects the set of devices allowed to generate IBIs.
Also update when IBIs are freed, to cover the corner case when an IBI is
freed without first being disabled (e.g. oldedev in
i3c_master_add_i3c_dev_locked()).

Move i3c_hci_addr_to_dev() into core.c, reimplement it using the new
array, and add a lockdep assertion to enforce that hci->lock is held
by callers.

Demote a message in PIO and DMA IBI handling, from an error to a debug
message, because there is a race window when the condition can arise
normally.

## References
- https://git.kernel.org/stable/c/650716f23eac488c6696babdc7805f6a6b7427ad
- https://git.kernel.org/stable/c/8f851cab401c28287d536b1347d76f6e219c0db6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72454.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
