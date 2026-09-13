# [C] spi: fsl-lpspi: terminate the RX channel on TX prepare failure path

## Summary
Severity: Critical
Advisory: CVE-2026-64303
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64303
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: fsl-lpspi: terminate the RX channel on TX prepare failure path

When dmaengine_prep_slave_sg() fails for the TX channel, the error path
terminates the TX DMA channel but leaves the RX channel running. Since
the RX channel was already submitted and issued prior to preparing
the TX descriptor, returning -EINVAL causes the SPI core to unmap the
DMA buffers while the RX DMA engine continues writing to them, leading
to potential memory corruption or use-after-free.

Terminate the RX channel before returning on the TX prepare failure path.

## References
- https://git.kernel.org/stable/c/01980b5da56e573d62798d0ff6c86bcaa2b22cbe
- https://git.kernel.org/stable/c/808033d80d5c9f8adf7e8de9317389270ce13430
- https://git.kernel.org/stable/c/9d000bdd250d649a11cd7f733175686877344582
- https://git.kernel.org/stable/c/ad370d1c7a9a832f77b2341513cd31188c9443af
- https://git.kernel.org/stable/c/af39a2698f69b584d14a00cffe0f51a2caa15337
- https://git.kernel.org/stable/c/cce2063404b2341e7b2bbf85eddfcd70a31a0033
- https://git.kernel.org/stable/c/d5c1060218a3749c8a18b36f8169d910fce20639
- https://git.kernel.org/stable/c/e65505d91fa036a238968e4c10744244d1b968c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64303.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64303
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
