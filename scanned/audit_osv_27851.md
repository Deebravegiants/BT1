# [H] pds_core: Prevent race issues involving the adminq

## Summary
Severity: High
Advisory: CVE-2024-26623
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2024-26623
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

pds_core: Prevent race issues involving the adminq

There are multiple paths that can result in using the pdsc's
adminq.

[1] pdsc_adminq_isr and the resulting work from queue_work(),
    i.e. pdsc_work_thread()->pdsc_process_adminq()

[2] pdsc_adminq_post()

When the device goes through reset via PCIe reset and/or
a fw_down/fw_up cycle due to bad PCIe state or bad device
state the adminq is destroyed and recreated.

A NULL pointer dereference can happen if [1] or [2] happens
after the adminq is already destroyed.

In order to fix this, add some further state checks and
implement reference counting for adminq uses. Reference
counting was used because multiple threads can attempt to
access the adminq at the same time via [1] or [2]. Additionally,
multiple clients (i.e. pds-vfio-pci) can be using [2]
at the same time.

The adminq_refcnt is initialized to 1 when the adminq has been
allocated and is ready to use. Users/clients of the adminq
(i.e. [1] and [2]) will increment the refcnt when they are using
the adminq. When the driver goes into a fw_down cycle it will
set the PDSC_S_FW_DEAD bit and then wait for the adminq_refcnt
to hit 1. Setting the PDSC_S_FW_DEAD before waiting will prevent
any further adminq_refcnt increments. Waiting for the
adminq_refcnt to hit 1 allows for any current users of the adminq
to finish before the driver frees the adminq. Once the
adminq_refcnt hits 1 the driver clears the refcnt to signify that
the adminq is deleted and cannot be used. On the fw_up cycle the
driver will once again initialize the adminq_refcnt to 1 allowing
the adminq to be used again.

## References
- https://git.kernel.org/stable/c/22cd6046eb2148b18990257505834dd45c672a1b
- https://git.kernel.org/stable/c/5939feb63ea1f011027576c64b68b681cbad31ca
- https://git.kernel.org/stable/c/7e82a8745b951b1e794cc780d46f3fbee5e93447
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26623.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26623
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
