# [H] spi: microchip-core: ensure TX and RX FIFOs are empty at start of a transfer

## Summary
Severity: High
Advisory: CVE-2024-42279
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42279
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: microchip-core: ensure TX and RX FIFOs are empty at start of a transfer

While transmitting with rx_len == 0, the RX FIFO is not going to be
emptied in the interrupt handler. A subsequent transfer could then
read crap from the previous transfer out of the RX FIFO into the
start RX buffer. The core provides a register that will empty the RX and
TX FIFOs, so do that before each transfer.

## References
- https://git.kernel.org/stable/c/3feda3677e8bbe833c3a62a4091377a08f015b80
- https://git.kernel.org/stable/c/45e03d35229b680b79dfea1103a1f2f07d0b5d75
- https://git.kernel.org/stable/c/9cf71eb0faef4bff01df4264841b8465382d7927
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42279.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42279
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
