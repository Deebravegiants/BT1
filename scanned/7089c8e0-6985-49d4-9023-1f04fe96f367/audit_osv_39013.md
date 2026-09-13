# [H] i3c: mipi-i3c-hci: Fix race in DMA ring dequeue

## Summary
Severity: High
Advisory: CVE-2026-43353
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43353
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

i3c: mipi-i3c-hci: Fix race in DMA ring dequeue

The HCI DMA dequeue path (hci_dma_dequeue_xfer()) may be invoked for
multiple transfers that timeout around the same time.  However, the
function is not serialized and can race with itself.

When a timeout occurs, hci_dma_dequeue_xfer() stops the ring, processes
incomplete transfers, and then restarts the ring.  If another timeout
triggers a parallel call into the same function, the two instances may
interfere with each other - stopping or restarting the ring at unexpected
times.

Add a mutex so that hci_dma_dequeue_xfer() is serialized with respect to
itself.

## References
- https://git.kernel.org/stable/c/1dca8aee80eea76d2aae21265de5dd64f6ba0f09
- https://git.kernel.org/stable/c/4faa1e9c67a2229f6749190aedaf88ce0391efd2
- https://git.kernel.org/stable/c/b684b420a5bb0ea1b0e13abfdb8ce41c5266e62e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43353.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43353
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
