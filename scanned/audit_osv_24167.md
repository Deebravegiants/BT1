# [M] i2c: designware: Fix handling of real but unexpected device interrupts

## Summary
Severity: Medium
Advisory: CVE-2022-50370
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50370
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: designware: Fix handling of real but unexpected device interrupts

Commit c7b79a752871 ("mfd: intel-lpss: Add Intel Alder Lake PCH-S PCI
IDs") caused a regression on certain Gigabyte motherboards for Intel
Alder Lake-S where system crashes to NULL pointer dereference in
i2c_dw_xfer_msg() when system resumes from S3 sleep state ("deep").

I was able to debug the issue on Gigabyte Z690 AORUS ELITE and made
following notes:

- Issue happens when resuming from S3 but not when resuming from
  "s2idle"
- PCI device 00:15.0 == i2c_designware.0 is already in D0 state when
  system enters into pci_pm_resume_noirq() while all other i2c_designware
  PCI devices are in D3. Devices were runtime suspended and in D3 prior
  entering into suspend
- Interrupt comes after pci_pm_resume_noirq() when device interrupts are
  re-enabled
- According to register dump the interrupt really comes from the
  i2c_designware.0. Controller is enabled, I2C target address register
  points to a one detectable I2C device address 0x60 and the
  DW_IC_RAW_INTR_STAT register START_DET, STOP_DET, ACTIVITY and
  TX_EMPTY bits are set indicating completed I2C transaction.

My guess is that the firmware uses this controller to communicate with
an on-board I2C device during resume but does not disable the controller
before giving control to an operating system.

I was told the UEFI update fixes this but never the less it revealed the
driver is not ready to handle TX_EMPTY (or RX_FULL) interrupt when device
is supposed to be idle and state variables are not set (especially the
dev->msgs pointer which may point to NULL or stale old data).

Introduce a new software status flag STATUS_ACTIVE indicating when the
controller is active in driver point of view. Now treat all interrupts
that occur when is not set as unexpected and mask all interrupts from
the controller.

## References
- https://git.kernel.org/stable/c/301c8f5c32c8fb79c67539bc23972dc3ef48024c
- https://git.kernel.org/stable/c/7fa5304c4b5b425d4a0b3acf10139a7f6108a85f
- https://git.kernel.org/stable/c/a206f7fbe9589c60fafad12884628c909ecb042f
- https://git.kernel.org/stable/c/aa59ac81e859006d3a1df035a19b3f2089110f93
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50370.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50370
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
