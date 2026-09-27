# [H] ALSA: us144mkii: capture_urb_complete: redundant usb_anchor_urb corrupts anchor list on each resubmission

## Summary
Severity: High
Advisory: CVE-2026-64601
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64601
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: us144mkii: capture_urb_complete: redundant usb_anchor_urb corrupts anchor list on each resubmission

In capture_urb_complete(), usb_anchor_urb() is called on every
completion callback, but the URB is already anchored from the
initial submission in tascam_trigger_start(). Each redundant call
corrupts the anchor's doubly-linked list and inflates the URB
refcount. When usb_kill_anchored_urbs() traverses the list during
stream stop / suspend / disconnect, the corrupted list leads to
use-after-free.

Remove the redundant usb_anchor_urb() from the resubmit path.

## References
- https://git.kernel.org/stable/c/16f14f55141d4c55c3f321f93c328fff7cd6860a
- https://git.kernel.org/stable/c/5cff1529a2f9b3461a7f5a6e36a86682fc290534
- https://git.kernel.org/stable/c/ab1db64912428cdf06a4f9542e16e0575e9ad59f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64601.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64601
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
