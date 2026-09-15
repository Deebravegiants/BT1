# [M] irqchip/gicv3: Workaround for NVIDIA erratum T241-FABRIC-4

## Summary
Severity: Medium
Advisory: CVE-2023-53383
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53383
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gicv3: Workaround for NVIDIA erratum T241-FABRIC-4

The T241 platform suffers from the T241-FABRIC-4 erratum which causes
unexpected behavior in the GIC when multiple transactions are received
simultaneously from different sources. This hardware issue impacts
NVIDIA server platforms that use more than two T241 chips
interconnected. Each chip has support for 320 {E}SPIs.

This issue occurs when multiple packets from different GICs are
incorrectly interleaved at the target chip. The erratum text below
specifies exactly what can cause multiple transfer packets susceptible
to interleaving and GIC state corruption. GIC state corruption can
lead to a range of problems, including kernel panics, and unexpected
behavior.

>From the erratum text:
  "In some cases, inter-socket AXI4 Stream packets with multiple
  transfers, may be interleaved by the fabric when presented to ARM
  Generic Interrupt Controller. GIC expects all transfers of a packet
  to be delivered without any interleaving.

  The following GICv3 commands may result in multiple transfer packets
  over inter-socket AXI4 Stream interface:
   - Register reads from GICD_I* and GICD_N*
   - Register writes to 64-bit GICD registers other than GICD_IROUTERn*
   - ITS command MOVALL

  Multiple commands in GICv4+ utilize multiple transfer packets,
  including VMOVP, VMOVI, VMAPP, and 64-bit register accesses."

  This issue impacts system configurations with more than 2 sockets,
  that require multi-transfer packets to be sent over inter-socket
  AXI4 Stream interface between GIC instances on different sockets.
  GICv4 cannot be supported. GICv3 SW model can only be supported
  with the workaround. Single and Dual socket configurations are not
  impacted by this issue and support GICv3 and GICv4."


Writing to the chip alias region of the GICD_In{E} registers except
GICD_ICENABLERn has an equivalent effect as writing to the global
distributor. The SPI interrupt deactivate path is not impacted by
the erratum.

To fix this problem, implement a workaround that ensures read accesses
to the GICD_In{E} registers are directed to the chip that owns the
SPI, and disable GICv4.x features. To simplify code changes, the
gic_configure_irq() function uses the same alias region for both read
and write operations to GICD_ICFGR.

## References
- https://git.kernel.org/stable/c/35727af2b15d98a2dd2811d631d3a3886111312e
- https://git.kernel.org/stable/c/867a4f6cf1a8f511c06e131477988b3b3e7a0633
- https://git.kernel.org/stable/c/86ba4f7b9f949e4c4bcb425f2a1ce490fea30df0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53383.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
