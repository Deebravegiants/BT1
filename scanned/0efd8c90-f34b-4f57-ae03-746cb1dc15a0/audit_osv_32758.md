# [H] usb: xhci: Fix isochronous Ring Underrun/Overrun event handling

## Summary
Severity: High
Advisory: CVE-2025-37882
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37882
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: xhci: Fix isochronous Ring Underrun/Overrun event handling

The TRB pointer of these events points at enqueue at the time of error
occurrence on xHCI 1.1+ HCs or it's NULL on older ones. By the time we
are handling the event, a new TD may be queued at this ring position.

I can trigger this race by rising interrupt moderation to increase IRQ
handling delay. Similar delay may occur naturally due to system load.

If this ever happens after a Missed Service Error, missed TDs will be
skipped and the new TD processed as if it matched the event. It could
be given back prematurely, risking data loss or buffer UAF by the xHC.

Don't complete TDs on xrun events and don't warn if queued TDs don't
match the event's TRB pointer, which can be NULL or a link/no-op TRB.
Don't warn if there are no queued TDs at all.

Now that it's safe, also handle xrun events if the skip flag is clear.
This ensures completion of any TD stuck in 'error mid TD' state right
before the xrun event, which could happen if a driver submits a finite
number of URBs to a buggy HC and then an error occurs on the last TD.

## References
- https://git.kernel.org/stable/c/16a7a8e6c47fea5c847beb696c8c21a7a44c1915
- https://git.kernel.org/stable/c/39a080a2925c81b0f1da0add44722ef2b78e5454
- https://git.kernel.org/stable/c/906dec15b9b321b546fd31a3c99ffc13724c7af4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37882.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37882
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
