# [H] spi: tegra210-quad: Fix timeout handling

## Summary
Severity: High
Advisory: CVE-2025-68746
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68746
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: tegra210-quad: Fix timeout handling

When the CPU that the QSPI interrupt handler runs on (typically CPU 0)
is excessively busy, it can lead to rare cases of the IRQ thread not
running before the transfer timeout is reached.

While handling the timeouts, any pending transfers are cleaned up and
the message that they correspond to is marked as failed, which leaves
the curr_xfer field pointing at stale memory.

To avoid this, clear curr_xfer to NULL upon timeout and check for this
condition when the IRQ thread is finally run.

While at it, also make sure to clear interrupts on failure so that new
interrupts can be run.

A better, more involved, fix would move the interrupt clearing into a
hard IRQ handler. Ideally we would also want to signal that the IRQ
thread no longer needs to be run after the timeout is hit to avoid the
extra check for a valid transfer.

## References
- https://git.kernel.org/stable/c/01bbf25c767219b14c3235bfa85906b8d2cb8fbc
- https://git.kernel.org/stable/c/551060efb156c50fe33799038ba8145418cfdeef
- https://git.kernel.org/stable/c/83309dd551cfd60a5a1a98d9cab19f435b44d46d
- https://git.kernel.org/stable/c/88db8bb7ed1bb474618acdf05ebd4f0758d244e2
- https://git.kernel.org/stable/c/b4e002d8a7cee3b1d70efad0e222567f92a73000
- https://git.kernel.org/stable/c/bb0c58be84f907285af45657c1d4847b960a12bf
- https://git.kernel.org/stable/c/c934e40246da2c5726d14e94719c514e30840df8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68746.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68746
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
