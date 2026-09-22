# [M] firewire: ohci: mask bus reset interrupts between ISR and bottom half

## Summary
Severity: Medium
Advisory: CVE-2024-36950
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36950
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

firewire: ohci: mask bus reset interrupts between ISR and bottom half

In the FireWire OHCI interrupt handler, if a bus reset interrupt has
occurred, mask bus reset interrupts until bus_reset_work has serviced and
cleared the interrupt.

Normally, we always leave bus reset interrupts masked. We infer the bus
reset from the self-ID interrupt that happens shortly thereafter. A
scenario where we unmask bus reset interrupts was introduced in 2008 in
a007bb857e0b26f5d8b73c2ff90782d9c0972620: If
OHCI_PARAM_DEBUG_BUSRESETS (8) is set in the debug parameter bitmask, we
will unmask bus reset interrupts so we can log them.

irq_handler logs the bus reset interrupt. However, we can't clear the bus
reset event flag in irq_handler, because we won't service the event until
later. irq_handler exits with the event flag still set. If the
corresponding interrupt is still unmasked, the first bus reset will
usually freeze the system due to irq_handler being called again each
time it exits. This freeze can be reproduced by loading firewire_ohci
with "modprobe firewire_ohci debug=-1" (to enable all debugging output).
Apparently there are also some cases where bus_reset_work will get called
soon enough to clear the event, and operation will continue normally.

This freeze was first reported a few months after a007bb85 was committed,
but until now it was never fixed. The debug level could safely be set
to -1 through sysfs after the module was loaded, but this would be
ineffectual in logging bus reset interrupts since they were only
unmasked during initialization.

irq_handler will now leave the event flag set but mask bus reset
interrupts, so irq_handler won't be called again and there will be no
freeze. If OHCI_PARAM_DEBUG_BUSRESETS is enabled, bus_reset_work will
unmask the interrupt after servicing the event, so future interrupts
will be caught as desired.

As a side effect to this change, OHCI_PARAM_DEBUG_BUSRESETS can now be
enabled through sysfs in addition to during initial module loading.
However, when enabled through sysfs, logging of bus reset interrupts will
be effective only starting with the second bus reset, after
bus_reset_work has executed.

## References
- https://git.kernel.org/stable/c/31279bbca40d2f40cb3bbb6d538ec9620a645dec
- https://git.kernel.org/stable/c/4f9cc355c328fc4f41cbd9c4cd58b235184fa420
- https://git.kernel.org/stable/c/5982887de60c1b84f9c0ca07c835814d07fd1da0
- https://git.kernel.org/stable/c/6fafe3661712b143d9c69a7322294bd53f559d5d
- https://git.kernel.org/stable/c/752e3c53de0fa3b7d817a83050b6699b8e9c6ec9
- https://git.kernel.org/stable/c/8643332aac0576581cfdf01798ea3e4e0d624b61
- https://git.kernel.org/stable/c/b3948c69d60279fce5b2eeda92a07d66296c8130
- https://git.kernel.org/stable/c/fa273f312334246c909475c5868e6daab889cc8c
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36950.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36950
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
