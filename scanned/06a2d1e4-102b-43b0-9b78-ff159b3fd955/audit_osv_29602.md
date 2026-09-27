# [H] serial: sc16is7xx: fix invalid FIFO access with special register set

## Summary
Severity: High
Advisory: CVE-2024-44950
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44950
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: sc16is7xx: fix invalid FIFO access with special register set

When enabling access to the special register set, Receiver time-out and
RHR interrupts can happen. In this case, the IRQ handler will try to read
from the FIFO thru the RHR register at address 0x00, but address 0x00 is
mapped to DLL register, resulting in erroneous FIFO reading.

Call graph example:
    sc16is7xx_startup(): entry
    sc16is7xx_ms_proc(): entry
    sc16is7xx_set_termios(): entry
    sc16is7xx_set_baud(): DLH/DLL = $009C --> access special register set
    sc16is7xx_port_irq() entry            --> IIR is 0x0C
    sc16is7xx_handle_rx() entry
    sc16is7xx_fifo_read(): --> unable to access FIFO (RHR) because it is
                               mapped to DLL (LCR=LCR_CONF_MODE_A)
    sc16is7xx_set_baud(): exit --> Restore access to general register set

Fix the problem by claiming the efr_lock mutex when accessing the Special
register set.

## References
- https://git.kernel.org/stable/c/6a6730812220a9a5ce4003eb347da1ee5abd06b0
- https://git.kernel.org/stable/c/7d3b793faaab1305994ce568b59d61927235f57b
- https://git.kernel.org/stable/c/cc6a3f35bc9b3a8da1b195420a2e8d9fdadfa831
- https://git.kernel.org/stable/c/dc5ead0e8fc5ef53b8553394d4aab60c277976b3
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44950.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44950
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
