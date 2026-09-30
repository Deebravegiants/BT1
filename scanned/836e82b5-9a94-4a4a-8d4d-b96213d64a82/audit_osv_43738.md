# [H] serial: qcom-geni: fix TX DMA buffer flush

## Summary
Severity: High
Advisory: CVE-2026-74655
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74655
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.154, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: qcom-geni: fix TX DMA buffer flush

When transmit flushing a qcom-geni UART during an ongoing TX DMA, the
UART gets stuck infinitely repeating corrupted TX DMA frames.

The DMA-mode uart_ops does not provide a flush_buffer callback, so an
in-flight transfer can complete after serial core has reset the transmit
kfifo, underflowing its length and resubmitting page-sized transfers
indefinitely. Add one that stops the transfer and clears tx_remaining
and tx_queued.

The stop path was also broken: it unmapped the buffer while the serial
engine could still read it, and never reset the TX DMA state machine.
Cancel the main sequencer command first, then reset the state machine
and wait for it before unmapping. Drop the early return so a pending
mapping is also cleaned up when the main command is inactive.

The bug can be triggered from userspace with a large write immediately
followed by TCOFLUSH. A following tcdrain will hang forever. The bug was
reproduced and this fix was validated on Arduino Uno Q (QRB2210)
using /dev/ttyHS1.

## References
- https://git.kernel.org/stable/c/1606abb7ce8c0cfef98c7e556b83c14e5d73c1bf
- https://git.kernel.org/stable/c/1c31e2377f4c1bb110ca7f6e597b2253a7440c37
- https://git.kernel.org/stable/c/313ae287442e5e8d3f7b53b73f37d384bda072d0
- https://git.kernel.org/stable/c/b1801c0d40f62778b613334de5840aba10a564d5
- https://git.kernel.org/stable/c/e3c04834ae1ab5e9cfbe8ac54ec734aa4774249d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74655.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74655
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
